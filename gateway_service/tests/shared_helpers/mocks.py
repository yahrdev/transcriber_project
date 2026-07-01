
#is no used for now
from app.models.micro_schemas import DownloaderResponseData, ConverterResponseData, TranscriberResponseData



def create_mocks(self, mock_validate_language, 
                     mock_extract_extension = None, 
                     lang_return_value = None, 
                     ext_return_value = None,
                     create_file_return_value = None,
                     need_downloading = False,
                     download_side_effect = None,
                     converter_side_effect = None,
                     ):
        
        mock_validate_language.return_value = lang_return_value

        if mock_extract_extension is not None:
            mock_extract_extension.return_value = ext_return_value

        if create_file_return_value is not None:
            self.jp.file_manager.create_tmp_file_path.return_value = create_file_return_value

        if need_downloading:
            self.jp.downloader.download.return_value = DownloaderResponseData(file_path=self.test_file_path_video,
                                                                                    file_name = self.test_file_name,
                                                                                    file_extension=self.test_file_extension_video)
            if download_side_effect is not None:
                self.jp.downloader.download.side_effect = download_side_effect

        self.jp.converter.convert.return_value = ConverterResponseData(file_path=self.test_file_path_audio,
                                                                                file_name = self.test_file_name,
                                                                                file_extension=self.test_file_extension_audio)
        if converter_side_effect is not None:
            self.jp.converter.convert.side_effect = converter_side_effect

        self.jp.transcriber.transcribe.return_value = TranscriberResponseData(file_path=self.test_file_path_transcibe)
