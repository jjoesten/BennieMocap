import logging
logger = logging.getLogger(__name__)

from pathlib import Path
from typing import Union, Dict
import numpy as np

from src.system.paths_and_filenames.folder_and_filenames import (
    SYNCHRONIZED_VIDEOS_FOLDER_NAME,
    ANNOTATED_VIDEOS_FOLDER_NAME,
    FRAMERATE_MATCHED_VIDEOS_FOLDER_NAME,
    OUTPUT_DATA_FOLDER_NAME,
    RAW_DATA_FOLDER_NAME,
    MEDIAPIPE_2D_NPY_FILENAME,
    RAW_MEDIAPIPE_3D_NPY_FILENAME,
    MEDIAPIPE_3D_NPY_FILENAME,
    MEDIAPIPE_REPROJECTION_ERROR_NPY_FILENAME
)
from src.system.paths_and_filenames.path_getters import (
    create_camera_calibration_file_name
)
from src.system.tests.video_tests import test_video_framerates, test_video_frame_counts
from src.tests.test_image_tracking_data_shape import test_image_tracking_data_shape

class SessionInfoModel:
    def __init__(self, session_folder_path: Union[str, Path]):
        if any(
            [
                Path(session_folder_path).name == SYNCHRONIZED_VIDEOS_FOLDER_NAME,
                Path(session_folder_path).name == ANNOTATED_VIDEOS_FOLDER_NAME,
                Path(session_folder_path).name == OUTPUT_DATA_FOLDER_NAME,
            ]
        ):
            session_folder_path = Path(session_folder_path).parent

        self._path = Path(session_folder_path)
        self._name = self._path.name

        self._calibration_toml_path = Path(self._path) / create_camera_calibration_file_name(session_name=self._name)

        self._session_status_checker = SessionStatusChecker(session_info_model=self)

    @property
    def path(self) -> str:
        return str(self._path)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def status_check(self) -> Dict[str, bool]:
        return self._session_status_checker.status_check
    
    @property
    def calibration_toml_path(self) -> str:
        return str(self._calibration_toml_path)
    
    @calibration_toml_path.setter
    def calibration_toml_path(self, path: Union[str, Path]):
        self._calibration_toml_path = str(path)

    @property
    def output_data_folder_path(self) -> Path:
        return Path(self._path) / OUTPUT_DATA_FOLDER_NAME
    
    @property
    def synchronized_videos_folder_path(self) -> Path:
        return Path(self._path) / SYNCHRONIZED_VIDEOS_FOLDER_NAME
    
    @property
    def framerate_matched_videos_folder_path(self) -> Path:
        return Path(self._path) / FRAMERATE_MATCHED_VIDEOS_FOLDER_NAME
    
    @property
    def annotated_videos_folder_path(self) -> Path:
        return Path(self._path) / ANNOTATED_VIDEOS_FOLDER_NAME
    
    @property
    def raw_data_folder_path(self) -> Path:
        return Path(self.output_data_folder_path) / RAW_DATA_FOLDER_NAME
    
    @property
    def mediapipe_2d_data_npy_file_path(self) -> Path:
        return Path(self._path) / OUTPUT_DATA_FOLDER_NAME / RAW_DATA_FOLDER_NAME / MEDIAPIPE_2D_NPY_FILENAME
    
    @property
    def mediapipe_3d_data_npy_file_path(self) -> Path:
        return Path(self._path) / OUTPUT_DATA_FOLDER_NAME / MEDIAPIPE_3D_NPY_FILENAME
    
    @property
    def raw_mediapipe_3d_data_npy_file_path(self) -> Path:
        return Path(self._path) / OUTPUT_DATA_FOLDER_NAME/ RAW_DATA_FOLDER_NAME / RAW_MEDIAPIPE_3D_NPY_FILENAME

    @property
    def mediapipe_reprojection_error_data_npy_file_path(self):
        return Path(self._path) / OUTPUT_DATA_FOLDER_NAME / RAW_DATA_FOLDER_NAME / MEDIAPIPE_REPROJECTION_ERROR_NPY_FILENAME



    @property
    def calibration_toml_check(self) -> bool:
        return self._session_status_checker.check_calibration_toml_status()

    @property
    def videos_framerate_status_check(self) -> bool:
        return self._session_status_checker.check_videos_framerate_status()
    
    @property
    def videos_synchronized_status_check(self) -> bool:
        return self._session_status_checker.check_videos_synchronized_status()
    
    @property
    def data2d_status_check(self) -> bool:
        return self._session_status_checker.check_data2d_status()
    
    @property
    def data3d_status_check(self) -> bool:
        return self._session_status_checker.check_data3d_status()
    
    @property
    def com_status_check(self) -> bool:
        return self._session_status_checker.check_com_data_status()
    



class SessionStatusChecker:
    def __init__(self, session_info_model: SessionInfoModel):
        self._session_info_model = session_info_model

    # TODO: Properly implement
    def status_check(self) -> Dict[str, Union[bool, str, float]]:
        return {
            "videos_framerate_status_check": self.check_videos_framerate_status(),
            "videos_synchronized_status_check": self.check_videos_synchronized_status(),
            "data2d_status_check": self.check_data2d_status(),
            "data3d_status_check": self.check_data3d_status(),
            "com_data_status_check": self.check_com_data_status(),
            "videos_info": {
                "number_synchronized_videos": 0,
                "number_frames_in_videos": 0,
            },
        }

    def check_videos_framerate_status(self) -> bool:
        try:
            # TODO: Test this, doesn't seem to be working
            test_video_framerates(self._session_info_model.synchronized_videos_folder_path)
            return True
        except AssertionError:
            return False
    
    def check_videos_synchronized_status(self) -> bool:
        try:
            test_video_frame_counts(self._session_info_model.synchronized_videos_folder_path)
            return True
        except AssertionError:
            return False
    
    def check_data2d_status(self) -> bool:
        try:
            test_image_tracking_data_shape(
                synchronized_video_folder_path=self._session_info_model.synchronized_videos_folder_path,
                image_tracking_data_file_path=self._session_info_model.mediapipe_2d_data_npy_file_path
            )
            return True
        except AssertionError:
            return False
    
    def check_data3d_status(self) -> bool:
        # TODO: Implement check_data3d_status
        return False
    
    def check_com_data_status(self) -> bool:
        # TODO: Implement check_com_data_status
        return False
    
    def check_calibration_toml_status(self) -> bool:
        toml_status = Path(self._session_info_model.calibration_toml_path).is_file()
        if not toml_status:
            logger.info("No calibration file found with session name, checking for other calibration files in the session path")
            toml_status = self._check_for_other_calibration_toml()
        return toml_status
    
    def _check_for_other_calibration_toml(self) -> bool:
        for file in Path(self._session_info_model.path).iterdir():
            if file.is_file() and file.name.endswith("camera_calibration.toml"):
                self._session_info_model.calibration_toml_path = str(file)
                logger.info(f"Found calibration file at: {self._session_info_model.calibration_toml_path}")
                return True
        return False