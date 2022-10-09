import os

from lightning import BuildConfig, CloudCompute, LightningWork
from lightning_app.storage import Drive
from pytube import YouTube


class YouTuber(LightningWork):
    """Handles downloading and extracting videos from YouTube."""

    def __init__(self, drive: Drive, base_dir: str = None):
        super().__init__(
            parallel=True,
            cloud_compute=CloudCompute("cpu"),
            cloud_build_config=BuildConfig(requirements=["pytube"]),
        )

        self.drive = drive
        self.base_dir = base_dir

    def run(self, youtube_url: str, echo_id: str):
        """Download a YouTube video and save it to the shared Drive."""
        if not youtube_url:
            raise ValueError("No YouTube URL provided.")

        if not echo_id:
            raise ValueError("No Echo ID provided.")

        YouTube(youtube_url).streams.filter(progressive=True, file_extension="mp4").order_by(
            "resolution"
        ).asc().first().download(output_path=self.base_dir, filename=echo_id)

        self.drive.put(self._get_drive_filepath(echo_id))

        os.remove(os.path.join(self.base_dir, echo_id))

    def _get_drive_filepath(self, echo_id: str):
        """Returns file path stored on the shared Drive."""
        # NOTE: Drive throws `SameFileError` when using absolute path in `put()`, so we use relative path.
        directory = self.base_dir.split(os.sep)[-1]

        return os.path.join(directory, echo_id)