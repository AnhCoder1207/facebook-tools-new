import random
from statemachine import StateMachine, State


class FacebookAutoMachine(StateMachine):
    """Define state"""
    home_page = State('home_page', initial=True)
    access_video = State("access_video")
    check_via = State("check_via")
    watch_video = State("watch_video")
    share_btn = State('share_btn')
    more_options = State('more_options')
    share_to_group = State('share_to_group')
    search_groups = State('search_groups')
    # join_group = State('join_group')
    # group_joined = State('group_joined')
    group_not_found = State('group_not_found')
    group_founded = State('group_founded')

    # define action
    opening_video = home_page.to(access_video)
    check_via_blocked = access_video.to(check_via)
    watching_video = check_via.to(watch_video)
    click_share_btn = watch_video.to(share_btn)
    click_more_options = share_btn.to(more_options)
    click_share_to_group = more_options.to(share_to_group)
    searching_groups = share_to_group.to(search_groups)
    joining_group = search_groups.to(group_not_found)
    select_this_group = search_groups.to(group_founded)

    def on_home_page(self):
        print('on_home_page')
        # self.opening_video()

    def on_opening_video(self):
        print('on_access_video')
        # self.run('check_via_blocked')
        return False

    def on_check_via_blocked(self):
        print('check_via_blocked')

    def on_check_via(self):
        print('on_check_via')

    def on_watch_video(self):
        print('on_watch_video')

    def on_share_btn(self):
        print('on_share_btn')

    def on_more_options(self):
        print('on_more_options')

    def on_share_to_group(self):
        print('on_share_to_group')

    def on_search_groups(self):
        print('on_search_groups')

    def on_group_not_found(self):
        print('on_group_not_found')
        pass

    def on_group_founded(self):
        print('on_group_founded')
        pass


if __name__ == '__main__':
    stm = FacebookAutoMachine(start_value='home_page')
    stm.opening_video()
    print(stm.current_state_value)
    stm.check_via_blocked()
    print(stm.current_state_value)