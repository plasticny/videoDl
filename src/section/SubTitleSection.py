from __future__ import annotations

from inquirer import prompt as inq_prompt, List as inq_List, Checkbox as inq_Checkbox
from colorama import Fore, Style
from collections.abc import Iterable
from enum import Enum

from section.Section import Section
from service.YtDlpHelper import Opts
from service.MetaData import MetaData, VideoMetaData
from service.structs import Subtitle

class SelectionMode(Enum):
  BATCH = 0
  ONE_BY_ONE = 1  

class SubTitleSection (Section):
  def run(self, md:MetaData, opts_ls:list[Opts]) -> list[Opts]:
    cp_opts_ls = [opts.copy() for opts in opts_ls]
    return super().run(self.__main, md=md, opts_ls=cp_opts_ls)
  
  def __main(self, md:MetaData, opts_ls:list[Opts]) -> list[Opts]:
    # get list of video meta data from md
    video_mds:list[VideoMetaData] = md.videos if md.isPlaylist() else [md]
    assert len(video_mds) == len(opts_ls)

    # set clear subtitle of all opts first
    for opts in opts_ls:
      opts.removeSubtitle()

    # mapping subtitle to position in opts_ls/video_mds, for selection usage
    sub_pos_map:dict[Subtitle, list[int]] = self.map_subs(video_mds)

    # if no subtitle available, return
    if len(sub_pos_map.keys()) == 0:
      print(f'{Fore.YELLOW}No subtitle available.{Style.RESET_ALL}')
      return opts_ls
    
    # select to write subtitle or not
    if not self.ask_write_sub():
      return opts_ls

    # choose selection mode
    if len(video_mds) == 1:
      # if only one video, select subtitle one by one
      opts_ls = self.one_by_one_select(video_mds, opts_ls)
    else:
      # if multiple videos, select batch or one by one
      if self.ask_selection_mode() == SelectionMode.BATCH.value:
        opts_ls = self.batch_select(sub_pos_map, opts_ls)
      else:
        opts_ls = self.one_by_one_select(video_mds, opts_ls)

    # check if user select subtitle for any video
    if not self.assigned_any_subtitle(opts_ls):
      print(f'{Fore.YELLOW}No subtitle selected.{Style.RESET_ALL}')
      return opts_ls

    # show selection result
    if self.ask_show_summary():
      self.show_selection_result(video_mds, opts_ls)

    # select write mode
    doEmbed, doBurn = self.select_write_mode()
    # print warning if not doEmbedSub and not doBurnSub:
    if not doEmbed and not doBurn:
      print(Fore.YELLOW)
      print('Warning: You did not choose any mode to write the subtitle, so the subtitle will not be shown in the video.')
      print(Style.RESET_ALL)
    else:
      for opts in opts_ls:
        opts.embedSubtitle = doEmbed
        opts.burnSubtitle = doBurn

    return opts_ls
  
  def one_by_one_select(self, video_mds:list[VideoMetaData], opts_ls:list[Opts]) -> list[Opts]:
    for idx, (md, opts) in enumerate(zip(video_mds, opts_ls)):
      # if no subtitle, skip
      if len(md.subtitles) == 0 and len(md.autoSubtitles) == 0:
        print(f'{Fore.YELLOW}No subtitle available for {md.title}.{Style.RESET_ALL}')
        continue

      # select subtitle
      print(f'{Fore.GREEN}Video {idx+1}/{len(video_mds)}{Style.RESET_ALL}')
      print(md.title)
      sub : Subtitle = self.select_sub(
        [*sorted(md.subtitles), *sorted(md.autoSubtitles)],
        can_skip=True, skip_msg='Skip this video'
      )
      if sub is None:
        # if choose to skip
        continue

      # assign subtitle to opts
      opts.setSubtitle(sub)

    return opts_ls

  def batch_select(self, sub_pos_map:dict[Subtitle, list[int]], opts_ls:list[Opts]) -> list[Opts]:
    """
      Procedure:
        Repeat until map empty / no more video without subtitle / choose to end selection.\n
          List union of all remaining video's subtitles.\n
          For each round, ask user to select a subtitle, and assign to all video that support it.\n
          After assigning, remove the subtitles that are no longer owned by any video from the map.\n

      Args:
        `sub_pos_map`\n
        `key`: subtitle; `value`: list of position in opts_ls/video_mds that support the subtitle.\n
        The value of sub_pos_map are treated as stacks.\n
        After assign a subtitle, pop every stack until reach the video of the idx is not assigned subtitle, or stack empty.\n
        If the stack is empty, remove the subtitle from map.\n

        `opts_ls`\n
        All video's download options. The selected subtitle will be assigned to the corresponding opts.\n
    """
    # the number of video that does not have subtitle
    no_sub_cnt:int = len(opts_ls)
    # copy sub_pos_map to prevent changing the original one
    sub_pos_map = sub_pos_map.copy()

    # keep selecting until the map empty
    # the map will also be empty if all video assigned subtitle
    while len(sub_pos_map) > 0:
      sub:Subtitle = self.select_sub(sorted(sub_pos_map.keys()), can_skip=True, skip_msg='End selection')

      # if choose to end the selection, break
      if sub is None:
        break

      # assign subtitle to the corresponding opts
      assigned_cnt:int = 0
      for idx in sub_pos_map[sub]:
        if opts_ls[idx].hasSubtitle():
          continue
        opts_ls[idx].setSubtitle(sub)
        assigned_cnt += 1
      no_sub_cnt -= assigned_cnt
      assert no_sub_cnt >= 0

      print(f'{Fore.GREEN}The subtitle is applied to {assigned_cnt} video(s){Style.RESET_ALL}')
      print(f'{Fore.YELLOW}{no_sub_cnt}{Style.RESET_ALL} video(s) left.')
      print()

      # remove subtitle from map
      del sub_pos_map[sub]
      
      # update stacks in the map
      empty_keys = []
      for s, pos_ls in sub_pos_map.items():
        # pop every stack until reach the video of the idx is not assigned subtitle, or stack empty
        while len(pos_ls) > 0 and opts_ls[pos_ls[-1]].hasSubtitle():
          pos_ls.pop()
        if len(pos_ls) == 0:
          empty_keys.append(s)
      # remove subtitle if stack is empty
      for k in empty_keys:
        del sub_pos_map[k]

    return opts_ls

  def map_subs(self, video_mds:list[VideoMetaData]) -> dict[Subtitle, list[int]]:
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

  def assigned_any_subtitle(self, opts_ls:list[Opts]) -> bool:
    for opts in opts_ls:
      if opts.hasSubtitle():
        return True
    return False

  def show_selection_result(self, video_mds:list[VideoMetaData], opts_ls:list[Opts]) -> None:
    for idx, md in enumerate(video_mds):
      print(f'{Fore.GREEN}Video {idx+1}/{len(video_mds)}{Style.RESET_ALL}')
      print(md.title)
      print(opts_ls[idx].subtitle)
      print()
    print()

  # ==================== Inquiry functions ==================== #

  def ask_write_sub(self) -> bool:
    """
      Ask user to select whether to write subtitle
    """
    doWriteSub = inq_prompt([
      inq_List(
        'writeSub', message=f'{Fore.GREEN}Found subtitle(s). {Fore.CYAN}Write subtitle?{Style.RESET_ALL}', 
        choices=['Yes','No'], default='Yes'
      )
    ])['writeSub']
    return doWriteSub == 'Yes'

  def ask_selection_mode(self) -> int:
    """
      Ask user to select the mode of selecting subtitle

      Returns:
        0: batch select
        1: select one by one
    """
    batch_select_msg = 'Batch select (Select a perferred subtitle, and apply to videos that support it)'
    one_by_one_select_msg = 'Select one by one (Select a subtitle for each video)'
    ans = inq_prompt([
      inq_List(
        'selectMode', message=f'{Fore.CYAN}There are multiple videos. Choose the mode of selecting subtitle{Style.RESET_ALL}', 
        choices=[batch_select_msg, one_by_one_select_msg], 
        default=batch_select_msg
      )
    ])['selectMode']
    return SelectionMode.BATCH.value if ans == batch_select_msg else SelectionMode.ONE_BY_ONE.value
  
  def select_sub(self, subs:Iterable[Subtitle], can_skip:bool=False, skip_msg:str='') -> Subtitle:
    """
      Ask user to select a subtitle

      Returns:
        The selected subtitle. None if skipped.
    """
    if can_skip:
      skip_msg = f'{Fore.RED}{skip_msg}{Style.RESET_ALL}'
      choices = [skip_msg]
    choices.extend(subs)

    ans = inq_prompt([
      inq_List('sub', message=f'{Fore.CYAN}Select a subtitle{Style.RESET_ALL}', choices=choices),
    ])['sub']
    return None if ans == skip_msg else ans
  
  def ask_show_summary(self) -> bool:
    """
      Ask user to select whether to show the summary of selection
    """
    showSummary = inq_prompt([
      inq_List(
        'showSummary', message=f'{Fore.CYAN}Show the summary of selection?{Style.RESET_ALL}', 
        choices=['Yes','No'], default='Yes'
      )
    ])['showSummary']
    return showSummary == 'Yes'

  def select_write_mode(self) -> tuple[bool, bool]:
    """
      Ask user to select the mode of writing subtitle

      Returns:
        (do embed sub, do burn sub)
    """
    ans = inq_prompt([
      inq_Checkbox(
        'writeMode', message=f'{Fore.CYAN}Choose the mode of writing subtitle (Space to select/deselect, Enter to confirm){Style.RESET_ALL}',
        choices=['Embed', 'Burn'], default=['Embed', 'Burn']
      )
    ])['writeMode']
    return ('Embed' in ans, 'Burn' in ans)
  
  # ==================== End Inquiry functions ==================== #