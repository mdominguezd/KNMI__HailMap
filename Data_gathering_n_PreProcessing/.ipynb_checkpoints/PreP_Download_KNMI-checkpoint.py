import logging
import sys
import requests
import os

def download_KNMI(api_key, date, time):
    
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")
    
    api_url = "https://api.dataplatform.knmi.nl/open-data"
    api_version = "v1"
    
    
    def main_download():
        # Parameters
        max_keys = "1"

        filenames = []
        
        for radar_name in ["denhelder", "herwijnen"]:
            
            #radar parameters
            if radar_name == "denhelder":
              dataset_name = "radar_volume_denhelder"
              if str(time)[-2:] == '00':
                start_after_filename_prefix = f"RAD_NL61_VOL_NA_{date}{time-45:04d}.h5"
              else:
                start_after_filename_prefix = f"RAD_NL61_VOL_NA_{date}{time-5:04d}.h5"
              dataset_version = "2.0"
                
            elif radar_name == "herwijnen":
              dataset_name = "radar_volume_full_herwijnen"
              if str(time)[-2:] == '00':
                start_after_filename_prefix = f"RAD_NL62_VOL_NA_{date}{time-45:04d}.h5"
              else:
                start_after_filename_prefix = f"RAD_NL62_VOL_NA_{date}{time-5:04d}.h5"
              # start_after_filename_prefix = f"RAD_NL62_VOL_NA_{date}{time-5:04d}.h5"
              dataset_version = "1.0"
        
            # Use list files request to request file of the day.
            list_files_response = requests.get(
                f"{api_url}/{api_version}/datasets/{dataset_name}/versions/{dataset_version}/files",
                headers={"Authorization": api_key},
                params={"maxKeys": max_keys, "startAfterFilename": start_after_filename_prefix},
            )
            list_files = list_files_response.json()
        
            logger.info(f"List files response:\n{list_files}")
            dataset_files = list_files.get("files")
        
            # Retrieve first file in the list files response
            filename = dataset_files[0].get("filename")
            
            filenames.append(filename)
            
            logger.info(f"Retrieve file with name: {filename}")
            endpoint = f"{api_url}/{api_version}/datasets/{dataset_name}/versions/{dataset_version}/files/{filename}/url"
            get_file_response = requests.get(endpoint, headers={"Authorization": api_key})
            if get_file_response.status_code != 200:
                logger.error("Unable to retrieve download url for file")
                logger.error(get_file_response.text)
                sys.exit(1)
        
            download_url = get_file_response.json().get("temporaryDownloadUrl")
            download_file_from_temporary_download_url(download_url, filename)

        return filenames
    
    def download_file_from_temporary_download_url(download_url, filename):
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception:
            logger.exception("Unable to download file using download URL")
            sys.exit(1)
    
        logger.info(f"Successfully downloaded dataset file to {filename}")
    
    filename = main_download()

    return filename