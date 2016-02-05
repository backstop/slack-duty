import argparse
import pygerduty
import slacker
import yaml


def read_config(config_file):
    with open(config_file) as fp:
        return yaml.load(fp)


def get_slack_user_id_by_pagerduty_schedule(slack, pagerduty, schedule_id):
    email = get_on_call_email(pagerduty, schedule_id)
    return get_slack_user_by_email(slack, email)


def get_slack_user_by_email(slack, email):
    users = [u for u in slack.users.list().body.get('members', []) if u.get('profile', {}).get('email', None) == email]
    if len(users) == 1:
        return users[0]['id']
    elif len(users) > 1:
        raise RuntimeError('Slack gave us duplicate users for a single email {}'.format(email))
    else:
        return None


def get_on_call_email(pagerduty, schedule_id):
    schedule = pagerduty.schedules.show(schedule_id)
    if not schedule:
        raise RuntimeError('No matching Pagerduty schedule {}'.format(schedule_id))
    return schedule.schedule_layers[0].schedule_users[0].user.email


def update_usergroup(slack, usergroup, group_desc, user_id):
    # slack doesn't like updating the name to the same name
    slack.usergroups.update(usergroup['id'], description=group_desc)
    slack.usergroups.users.update(usergroup['id'], [user_id])


def create_usergroup(slack, handle, group_name, group_desc, user_id):
    resp = slack.usergroups.create(group_name, handle=handle, description=group_desc)
    usergroup_id = resp.body['usergroup']['id']
    slack.usergroups.users.update(usergroup_id, [user_id])


def slack_duty(config_file):
    config = read_config(config_file)
    slack = slacker.Slacker(config['slack_api_token'])
    slack.users.list()
    pagerduty = pygerduty.PagerDuty('backstop', api_token=config['pagerduty_api_token'])
    usergroups = slack.usergroups.list(include_disabled=True).body['usergroups']
    for handle, group_config in config.get('usergroups', {}).items():
        group_config.setdefault('slack_group_name', handle)
        matching_groups = [ug for ug in usergroups if ug['handle'] == handle]
        if len(matching_groups) > 1:
            raise RuntimeError('Slack gave us duplicate groups for a single handle {}'.format(handle))
        else:
            user_id = get_slack_user_id_by_pagerduty_schedule(slack, pagerduty, group_config['pagerduty_schedule'])
            group_desc = group_config.get('slack_group_description', None)
            group_name = group_config['slack_group_name']
            if len(matching_groups) == 1:
                update_usergroup(slack, matching_groups[0], group_desc, user_id)
            else:
                create_usergroup(slack, handle, group_name, group_desc, user_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')

    args = parser.parse_args()
    slack_duty(args.config_file)

if __name__ == '__main__':
    main()
