import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

# Adjust path to find execution folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "execution")))

# Import module under test
import dashboard_server

class StopLoopException(BaseException):
    pass

class TestSchedulerPublishing(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        self.mock_post_to_forum = MagicMock()
        self.mock_vote_on_poll = MagicMock()
        self.mock_like_forum_post = MagicMock()
        self.mock_add_forum_comment = MagicMock()
        self.mock_get_fresh_token = MagicMock(return_value="fresh_token_123")
        self.mock_run_auto_poster = MagicMock(return_value=True)

        # Apply patches
        self.patchers = [
            patch("post_to_forum.post_to_forum", self.mock_post_to_forum),
            patch("dashboard_server.vote_on_poll", self.mock_vote_on_poll),
            patch("dashboard_server.like_forum_post", self.mock_like_forum_post),
            patch("dashboard_server.add_forum_comment", self.mock_add_forum_comment),
            patch("dashboard_server.get_fresh_token", self.mock_get_fresh_token),
            patch("auto_forum_poster.run_auto_poster", self.mock_run_auto_poster),
            # Mock sleep to stop the while True loop on its first sleep call
            patch("time.sleep", side_effect=StopLoopException("Sleep triggered"))
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    def test_scheduled_post_publishing(self, mock_listdir, mock_isdir, mock_exists):
        """Test that a 'scheduled' post is published and comments/likes/votes are triggered."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        
        # os.listdir calls:
        # 1st call: list of bots in bots directory
        # 2nd call: list of company directories for the bot
        mock_listdir.side_effect = [
            ["test_bot"],        # os.listdir(bots_dir)
            ["test_company"]     # os.listdir(bot_path)
        ]

        profile_json = '{"bot_username": "mock_bot", "oauth_token": "mock_oauth", "refresh_token": "mock_refresh"}'
        company_json = '{"company_id": "mock_company_id", "company_name": "Mock Company"}'
        scheduler_json = '''{
            "master_switch_enabled": true,
            "scheduler_enabled": true,
            "autopilot_enabled": false,
            "experience_ids": ["mock_exp_id"],
            "active_slots": {
                "mon": {"enabled": true, "start": "00:00", "end": "23:59"},
                "tue": {"enabled": true, "start": "00:00", "end": "23:59"},
                "wed": {"enabled": true, "start": "00:00", "end": "23:59"},
                "thu": {"enabled": true, "start": "00:00", "end": "23:59"},
                "fri": {"enabled": true, "start": "00:00", "end": "23:59"},
                "sat": {"enabled": true, "start": "00:00", "end": "23:59"},
                "sun": {"enabled": true, "start": "00:00", "end": "23:59"}
            },
            "posts_published_today": 0,
            "max_posts_per_day": 5,
            "last_run_time": 0.0,
            "frequency_minutes": 0,
            "random_delay_max_minutes": 0
        }'''

        # Mock action database containing a scheduled post
        mock_actions = [
            {
                "id": "action_123",
                "type": "forum",
                "status": "scheduled",
                "company_id": "mock_company_id",
                "experience_id": "mock_exp_id",
                "title": "Scheduled Post Title",
                "content": "Scheduled Post Content",
                "options": ["Option A", "Option B"],
                "auto_vote": True,
                "auto_like_post": True,
                "auto_comment": True,
                "comment_text": "Mock Comment Text",
                "auto_like_comment": True
            }
        ]

        # Custom file opener mock to handle multiple files correctly by name
        def custom_mock_open(filename, mode="r", *args, **kwargs):
            content = ""
            if "profile.json" in filename:
                content = profile_json
            elif "company.json" in filename:
                content = company_json
            elif "scheduler_settings.json" in filename:
                content = scheduler_json
            
            mock_file = MagicMock()
            mock_file.read.return_value = content
            mock_file.__enter__.return_value = mock_file
            return mock_file

        # Mock return of post_to_forum to simulate successful publishing
        self.mock_post_to_forum.return_value = {"id": "post_mock_456"}
        self.mock_add_forum_comment.return_value = {"id": "comment_mock_789"}

        with patch("builtins.open", side_effect=custom_mock_open), \
             patch("dashboard_server.load_actions", return_value=mock_actions) as mock_load, \
             patch("dashboard_server.save_actions") as mock_save:
            
            # Run scheduler loop
            try:
                dashboard_server.run_forum_scheduler_loop()
            except StopLoopException:
                pass  # Successfully exited the loop

            # Assertions
            self.mock_post_to_forum.assert_called_once()
            call_kwargs = self.mock_post_to_forum.call_args[1]
            self.assertEqual(call_kwargs["title"], "Scheduled Post Title")
            self.assertEqual(call_kwargs["content"], "Scheduled Post Content")
            self.assertEqual(call_kwargs["company_id"], "mock_company_id")
            self.assertEqual(call_kwargs["bot_user_id"], "test_bot")

            # Check post-publication operations
            self.mock_vote_on_poll.assert_called_once()
            self.mock_like_forum_post.assert_any_call("post_mock_456", "fresh_token_123")
            self.mock_add_forum_comment.assert_called_once_with(
                "mock_exp_id",
                "post_mock_456",
                "Mock Comment Text",
                "fresh_token_123"
            )
            self.mock_like_forum_post.assert_any_call("comment_mock_789", "fresh_token_123")

            # Check action state is updated to approved
            mock_save.assert_called_once()
            saved_actions = mock_save.call_args[0][0]
            self.assertEqual(saved_actions[0]["status"], "approved")
            self.assertEqual(saved_actions[0]["post_id"], "post_mock_456")

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    def test_pending_post_is_skipped(self, mock_listdir, mock_isdir, mock_exists):
        """Test that a 'pending' draft post is NOT published and scheduler falls through."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.side_effect = [
            ["test_bot"],
            ["test_company"]
        ]

        profile_json = '{"bot_username": "mock_bot", "oauth_token": "mock_oauth", "refresh_token": "mock_refresh"}'
        company_json = '{"company_id": "mock_company_id", "company_name": "Mock Company"}'
        scheduler_json = '''{
            "master_switch_enabled": true,
            "scheduler_enabled": true,
            "autopilot_enabled": true,
            "experience_ids": ["mock_exp_id"],
            "active_slots": {
                "mon": {"enabled": true, "start": "00:00", "end": "23:59"},
                "tue": {"enabled": true, "start": "00:00", "end": "23:59"},
                "wed": {"enabled": true, "start": "00:00", "end": "23:59"},
                "thu": {"enabled": true, "start": "00:00", "end": "23:59"},
                "fri": {"enabled": true, "start": "00:00", "end": "23:59"},
                "sat": {"enabled": true, "start": "00:00", "end": "23:59"},
                "sun": {"enabled": true, "start": "00:00", "end": "23:59"}
            },
            "posts_published_today": 0,
            "max_posts_per_day": 5,
            "last_run_time": 0.0,
            "frequency_minutes": 0,
            "random_delay_max_minutes": 0
        }'''

        # Mock action database containing a pending (unapproved/unscheduled) draft post
        mock_actions = [
            {
                "id": "action_pending_123",
                "type": "forum",
                "status": "pending",
                "company_id": "mock_company_id",
                "experience_id": "mock_exp_id",
                "title": "Pending Post Title",
                "content": "Pending Post Content"
            }
        ]

        def custom_mock_open(filename, mode="r", *args, **kwargs):
            content = ""
            if "profile.json" in filename:
                content = profile_json
            elif "company.json" in filename:
                content = company_json
            elif "scheduler_settings.json" in filename:
                content = scheduler_json
            
            mock_file = MagicMock()
            mock_file.read.return_value = content
            mock_file.__enter__.return_value = mock_file
            return mock_file

        with patch("builtins.open", side_effect=custom_mock_open), \
             patch("dashboard_server.load_actions", return_value=mock_actions), \
             patch("dashboard_server.save_actions") as mock_save:
            
            try:
                dashboard_server.run_forum_scheduler_loop()
            except StopLoopException:
                pass

            # Assert that the pending post was NOT published
            self.mock_post_to_forum.assert_not_called()
            # Assert that scheduler fell through to Autopilot
            self.mock_run_auto_poster.assert_called_once_with(
                draft_mode=False,
                experience_id="mock_exp_id",
                bot_user_id="test_bot"
            )
            # Database should not be modified
            mock_save.assert_not_called()

if __name__ == "__main__":
    unittest.main()
