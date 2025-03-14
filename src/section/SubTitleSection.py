from __future__ import annotations
from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox # type: ignore
from colorama import Fore, Style
from collections.abc import Iterable
from enum import Enum
from typing import TypedDict, Optional, Sequence, Union

from src.section.Section import Section

from src.service.MetaData import VideoMetaData
from src.service.autofill import get_do_write_subtitle_autofill, get_sub_lang_autofill, get_sub_write_mode_autofill

from src.structs.video_info import Subtitle


class TSubtitleSectionRet (TypedDict):
  do_write_subtitle : bool
  do_embed : bool
  do_burn : bool
  subtitle_ls : Sequence[Optional[Subtitle]]


class SelectionMode(Enum):
  BATCH = 0
  ONE_BY_ONE = 1


class SubTitleSection (Section):
  @staticmethod
  def not_write_ret(md_ls:list[VideoMetaData]) -> TSubtitleSectionRet:
    return {
      'do_write_subtitle': False,
      'subtitle_ls': [ None for _ in range(len(md_ls)) ],
      'do_embed': False,
      'do_burn': False
    }
  
  def run (self, md_ls:list[VideoMetaData]) -> TSubtitleSectionRet: # type: ignore
    return super().run(self.__main, md_ls=md_ls)
  
  def __main(self, md_ls:list[VideoMetaData]) -> TSubtitleSectionRet:
    # mapping subtitle to position in opts_ls/video_mds, for selection usage
    sub_pos_map:dict[Subtitle, list[int]] = self.map_subs(md_ls)

    # if no subtitle available, return
    if len(sub_pos_map.keys()) == 0:
      print(f'{Fore.YELLOW}No subtitle available.{Style.RESET_ALL}')
      return SubTitleSection.not_write_ret(md_ls)
    
    # select to write subtitle or not
    if not self.ask_write_sub():
      return SubTitleSection.not_write_ret(md_ls)
    
    # select subtitle
    selection_res = self.control_sub_selection(md_ls, sub_pos_map)

    # check if user select subtitle for any video
    if not any(selection_res):
      print(f'{Fore.YELLOW}No subtitle selected.{Style.RESET_ALL}')
      return SubTitleSection.not_write_ret(md_ls)

    # show selection result
    # if self.ask_show_summary():
    #   self.show_selection_result(md_ls, selection_res)

    # select write mode
    doEmbed, doBurn = self.select_write_mode()
    # print warning if not doEmbedSub and not doBurnSub:
    if not doEmbed and not doBurn:
      print(Fore.YELLOW)
      print('Warning: You did not choose any mode to write the subtitle, so the subtitle will not be shown in the video.')
      print(Style.RESET_ALL)

    return {
      'do_write_subtitle': True,
      'do_embed': doEmbed,
      'do_burn': doBurn,
      'subtitle_ls': selection_res
    }

  def control_sub_selection (self, md_ls:list[VideoMetaData], sub_pos_map:dict[Subtitle, list[int]]) -> list[Optional[Subtitle]]:
    """
      Control the mode to select subtitle, also run the selection process
      Return: a list of selected subtitle
    """
    # check if autofill
    sub_select_autofill = get_sub_lang_autofill()
    if sub_select_autofill is not None:
      print(f'{Fore.GREEN}Autofill config found, subtitle is selected automatically{Style.RESET_ALL}\n')
      return self.autofill_sub(md_ls, sub_select_autofill)

    # if only one video, select one by one
    if len(md_ls) == 1:
      return self.one_by_one_select(md_ls)

    # ask user to choose to select in batch or one by one
    if self.ask_selection_mode() == SelectionMode.BATCH.value:
      return self.batch_select(sub_pos_map, len(md_ls))
    else:
      return self.one_by_one_select(md_ls)
  
  def one_by_one_select(self, video_mds:list[VideoMetaData]) -> list[Optional[Subtitle]]:
    res: list[Optional[Subtitle]] = []
    
    for idx, md in enumerate(video_mds):
      # if no subtitle, skip
      if len(md.subtitles) == 0 and len(md.autoSubtitles) == 0:
        print(f'{Fore.YELLOW}No subtitle available for {md.title}.{Style.RESET_ALL}')
        res.append(None)
        continue

      # select subtitle
      print(f'{Fore.GREEN}Video {idx+1}/{len(video_mds)}{Style.RESET_ALL}')
      print(md.title)
      sub: Optional[Subtitle] = self.select_sub(
        [*sorted(md.subtitles), *sorted(md.autoSubtitles)],
        can_skip=True, skip_msg='Skip this video'
      )
      res.append(sub)

    return res

  def batch_select(self, sub_pos_map:dict[Subtitle, list[int]], video_num:int) -> list[Optional[Subtitle]]:
    """
      Procedure:
        Repeat until map empty / no more video without subtitle / choose to end selection.\n
          List union of all remaining video's subtitles.\n
          For each round, ask user to select a subtitle, and assign to all video that support it.\n
          After assigning, remove the subtitles that are no longer owned by any video from the map.\n

      Args:
        `sub_pos_map`\n
        key: subtitle; value: list of position in video_mds that support the subtitle.\n
        The value of sub_pos_map are treated as stacks.\n
        After assign a subtitle, pop every stack until reach the video of the idx is not assigned subtitle, or stack empty.\n
        If the stack is empty, remove the subtitle from map.\n
        
        `video_num`\n
        The number of video that should be assigned subtitle.\n
        
      Return:
        A list of subtitle that each video should use. The position is mapped to the metadata list.
    """
    # copy sub_pos_map to prevent changing the original one
    sub_pos_map = sub_pos_map.copy()

    # result list
    res : list[Optional[Subtitle]] = [ None for _ in range(video_num) ]
    # the number of video that does not have subtitle
    no_sub_cnt:int = len(res)

    # keep selecting until the map empty
    # the map will also be empty if all video assigned subtitle
    while len(sub_pos_map) > 0:
      # sub_pos_map.keys() is the union of all remaining video's subtitles
      sub: Optional[Subtitle] = self.select_sub(sorted(sub_pos_map.keys()), can_skip=True, skip_msg='End selection')

      # if choose to end the selection, break
      if sub is None:
        break

      # assign subtitle to the corresponding opts
      assigned_cnt:int = 0
      for idx in sub_pos_map[sub]:
        if res[idx] is not None:
          continue
        res[idx] = sub
        assigned_cnt += 1
      no_sub_cnt -= assigned_cnt
      assert no_sub_cnt >= 0

      print(f'{Fore.GREEN}The subtitle is applied to {assigned_cnt} video(s){Style.RESET_ALL}')
      print(f'{Fore.YELLOW}{no_sub_cnt}{Style.RESET_ALL} video(s) left.')
      print()

      # remove subtitle from map
      del sub_pos_map[sub]
      
      # update stacks in the map
      empty_keys: list[Subtitle] = []
      for s, pos_ls in sub_pos_map.items():
        # pop every stack until reach the video of the idx is not assigned subtitle, or stack empty
        while len(pos_ls) > 0 and res[pos_ls[-1]] is not None:
          pos_ls.pop()
        if len(pos_ls) == 0:
          empty_keys.append(s)
      # remove subtitle if stack is empty
      for k in empty_keys:
        del sub_pos_map[k]

    return res

  def map_subs(self, video_mds:list[VideoMetaData]) -> dict[Subtitle, list[int]]:
    """
      Construct a map from subtitle to position in video_mds that support the subtitle
    """
    sub_pos_map:dict[Subtitle, list[int]] = dict()

    for idx, md in enumerate(video_mds):
      def store_sub(sub:Subtitle):
        # store to map
        if sub not in sub_pos_map:
          sub_pos_map[sub] = []
        sub_pos_map[sub].append(idx)

      for sub in md.subtitles:
        store_sub(sub)
      for sub in md.autoSubtitles:
        store_sub(sub)

    return sub_pos_map

  def autofill_sub(self, video_mds:list[VideoMetaData], config_preferred_ls:list[str]) -> list[Optional[Subtitle]]:
    """
      Args:
        `config_preferred_ls`: list of preferred subtitle code from config file
    """             
    res: list[Optional[Subtitle]] = []
    for md in video_mds:
      available_sub : dict[str, Subtitle] = {}
      for sub in md.subtitles:
        available_sub[sub.code] = sub
      for sub in md.autoSubtitles:
        available_sub[sub.code] = sub
      
      selected_sub = None
      for code in config_preferred_ls:
        if code in available_sub:
          selected_sub = available_sub[code]
          break
      res.append(selected_sub)

    return res

  def show_selection_result(self, video_mds:list[VideoMetaData], selection_res:list[Subtitle]) -> None:
    for idx, (md, sub) in enumerate(zip(video_mds, selection_res)):
      print(f'{Fore.GREEN}Video {idx+1}/{len(video_mds)}{Style.RESET_ALL}')
      print(md.title)
      print(sub if sub is not None else 'No subtitle selected')
      print()
    print()


  # ==================== Inquiry functions ==================== #
  def ask_write_sub(self) -> bool:
    """
      Ask user to select whether to write subtitle
    """
    autofill = get_do_write_subtitle_autofill()
    if autofill is not None:
      if autofill == False:
        print(f'{Fore.GREEN}do_write_subtitle is set False in Autofill config, subtitle will not be written{Style.RESET_ALL}\n')
      return autofill
    
    return inq_prompt([
      inq_List(
        'writeSub', message=f'{Fore.GREEN}Found subtitle(s). {Fore.CYAN}Write subtitle?{Style.RESET_ALL}', 
        choices=['Yes','No'], default='Yes'
      )
    ])['writeSub'] == 'Yes' # type: ignore

  def ask_selection_mode(self) -> int:
    """
      Ask user to select the mode of selecting subtitle

      Returns:
        0: batch select
        1: select one by one
    """
    batch_select_msg = 'Batch select (Select a perferred subtitle, and apply to videos that support it)'
    one_by_one_select_msg = 'Select one by one (Select a subtitle for each video)'
    ans: str = inq_prompt([ # type: ignore
      inq_List(
        'selectMode', message=f'{Fore.CYAN}There are multiple videos. Choose the mode of selecting subtitle{Style.RESET_ALL}', 
        choices=[batch_select_msg, one_by_one_select_msg], 
        default=batch_select_msg
      )
    ])['selectMode'] # type: ignore
    return SelectionMode.BATCH.value if ans == batch_select_msg else SelectionMode.ONE_BY_ONE.value
  
  def select_sub(self, subs:Iterable[Subtitle], can_skip:bool=False, skip_msg:str='') -> Optional[Subtitle]:
    """
      Ask user to select a subtitle

      Returns:
        The selected subtitle. None if skipped.
    """
    choices: list[Union[str, Subtitle]] = []
    if can_skip:
      skip_msg = f'{Fore.RED}{skip_msg}{Style.RESET_ALL}'
      choices = [skip_msg]
    choices.extend(subs)

    ans: Union[str, Subtitle] = inq_prompt([ # type: ignore
      inq_List('sub', message=f'{Fore.CYAN}Select a subtitle{Style.RESET_ALL}', choices=choices),
    ])['sub'] # type: ignore
    if ans == skip_msg:
      return None
    assert isinstance(ans, Subtitle)
    return ans
  
  def ask_show_summary(self) -> bool:
    """
      Ask user to select whether to show the summary of selection
    """
    return inq_prompt([
      inq_List(
        'showSummary', message=f'{Fore.CYAN}Show the summary of selection?{Style.RESET_ALL}', 
        choices=['Yes','No'], default='Yes'
      )
    ])['showSummary'] == 'Yes' # type: ignore

  def select_write_mode(self) -> tuple[bool, bool]:
    """
      Ask user to select the mode of writing subtitle

      Returns:
        (do embed sub, do burn sub)
    """
    autofill = get_sub_write_mode_autofill()
    if autofill is not None:
      print(f'{Fore.GREEN}Autofill config found{Style.RESET_ALL}')
      print(f'Embed: {autofill[0]}, Burn: {autofill[1]}')
      print()
      return autofill[0], autofill[1]
    
    ans: list[str] = inq_prompt([ # type: ignore
      inq_Checkbox(
        'writeMode', message=f'{Fore.CYAN}Choose the mode of writing subtitle (Space to select/deselect, Enter to confirm){Style.RESET_ALL}',
        choices=['Embed', 'Burn'], default=['Embed', 'Burn']
      )
    ])['writeMode'] # type: ignore
    return ('Embed' in ans, 'Burn' in ans)  
  # ==================== End Inquiry functions ==================== #
