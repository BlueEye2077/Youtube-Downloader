import yt_dlp ;
from tqdm import tqdm

def tqdm_hook(status):
    if status['status'] == 'downloading':
        total = status.get('total_bytes') or status.get('total_bytes_estimate')
        downloaded = status.get('downloaded_bytes', 0)

        if not hasattr(tqdm_hook, 'bar') and total:
            tqdm_hook.bar = tqdm(
                total=total,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc='📥 Downloading',
                dynamic_ncols=True,
                leave=True,
            )

        if hasattr(tqdm_hook, 'bar'):
            tqdm_hook.bar.n = downloaded
            tqdm_hook.bar.refresh()

    elif status['status'] == 'finished':
        if hasattr(tqdm_hook, 'bar'):
            tqdm_hook.bar.n = tqdm_hook.bar.total
            tqdm_hook.bar.refresh()
            tqdm_hook.bar.close()
            del tqdm_hook.bar
        print(f"\n✅ Finished downloading: {status['filename']}")

class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"❌ Error: {msg}")

def get_available_qualities(video_url):
    yt_dlp_opts = {
        'listformats': True,
        'quiet': True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        # qualities_set= set() 
        reslution_dict ={}

        # file info all keys =>
        # dict_keys(['id', 'title', 'formats', 'thumbnails', 'thumbnail', 'description', 'channel_id', 'channel_url', 'duration', 'view_count', 'average_rating', 'age_limit', 'webpage_url', 'categories', 'tags', 'playable_in_embed', 'live_status', 'media_type', 'release_timestamp', '_format_sort_fields', 'automatic_captions', 'subtitles', 'comment_count', 'chapters', 'heatmap', 'like_count', 'channel', 'channel_follower_count', 'channel_is_verified', 'uploader', 'uploader_id', 'uploader_url', 'upload_date', 'timestamp', 'availability', 'original_url', 'webpage_url_basename', 'webpage_url_domain', 'extractor', 'extractor_key', 'playlist', 'playlist_index', 'display_id', 'fulltitle', 'duration_string', 'release_year', 'is_live', 'was_live', 'requested_subtitles', '_has_drm', 'epoch'])

        file_info=ydl.extract_info(video_url,download=False)
        
        # file_formats is a 'list' includes dicts with these keys =>
        # dict_keys(['asr', 'filesize', 'format_id', 'format_note', 'source_preference', 'fps', 'audio_channels',
        # 'height', 'quality', 'has_drm', 'tbr', 'filesize_approx', 'url', 'width', 'language', 'language_preference',
        # 'preference', 'ext', 'vcodec', 'acodec', 'dynamic_range', 'container', 'downloader_options', 'protocol', 
        # 'video_ext', 'audio_ext', 'abr', 'vbr', 'resolution', 'aspect_ratio', 'http_headers', 'format'])

        file_formats=file_info.get("formats","Formats Not Found")

        # f is one of dics inside the list
        for f in file_formats :
            # print(f"this is format id: {f.get('format_id','Format ID Not Found')}")
            # print(f"this is tbr: {f.get('tbr','TBR Not Found')} Kbps")
            # print(f"this is vcodec: {f.get('vcodec','VCodec Not Found')}")
            # print(f"this is acodec: {f.get('acodec','ACodec Not Found')}")
            # print(f"this is format note: {f.get('format_note','Format Note Not Found')}")
            # print(f"this is filesize: {f.get("filesize","Size Not Found")} bytes")
            # print (f"this is height: {f.get('height','height Not Found')}")
            # print(f"this is quality: {f.get('quality','Quality Not Found')}")
            # print(f"this is file size approx: {f.get('filesize_approx','Size Approx Not Found')} bytes")
            # print(f"this isresolution: {f.get('resolution','Resolution Not Found')}")
            # print(f"this is format {f.get('format','Format Not Found')}")
            # print(f"this is duration: {f.get('duration','Duration Not Found')} seconds")
            # print(f"this is calulated size: {(f.get('tbr') * 1024 / 8) * file_info.get('duration')} bytes" if f.get('tbr') and file_info.get('duration') else "N/A")
            # print("="*50)

            f_height = f.get('height',None)
            f_tbr=f.get("tbr",None)
            f_filesize=f.get("filesize",None)

            if f_height and f_height>= 144:
                if f_height not in reslution_dict:
                    reslution_dict.update({f_height:{"tbr":[],"filesize":[]}})

                if isinstance(f_tbr,(float , int)) and isinstance(f_filesize,(float , int)):
                    reslution_dict[f_height]["tbr"].append(f_tbr if isinstance(f_tbr,(float , int)) else 0 )
                    reslution_dict[f_height]["filesize"].append(f_filesize if isinstance(f_filesize,(float , int)) else 0)
            
    return reslution_dict

# ======================================================================================

def clear_empty_data(wanted_dict):
    wanted_remove_key=[]
    for key, value in wanted_dict.items():
        if value["filesize"] == []:
            wanted_remove_key.append(key)

    for i in wanted_remove_key:
        wanted_dict.pop(i)

    return wanted_dict

# ======================================================================================

def print_available_qualities(resolution_dict : dict):
    numbered_resolutions_dict={}
    try:
        if resolution_dict:
            print("Available Qualities:")
            print()
            for num, (key, value) in enumerate(resolution_dict.items(), start=1):
                video_size = max(value["filesize"])/(1024*1024)
                numbered_resolutions_dict.update({num:key})
                print(f"{num}-{key}p\t=> {video_size:.2f} MB") if len(str(int(video_size))) < 4 else print(f"{num}-{key}p\t=> {video_size/1024:.2f} GB") 
        
    except Exception as e:
        print(f"An error occurred while getting available qualities: {e}")
    
    else:
        return numbered_resolutions_dict
        
# ======================================================================================

def download_video(video_url, wanted_quality,subtitle=False,thumbnail=False):
    yt_dlp_opts = {
        'format': f'bestvideo[height<={wanted_quality}]+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        "no_warnings": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
        "concurrent_fragment_downloads":10,
        'throttled_rate': None,
        "embedthumbnail":True,
        "logger": MyLogger(),
        "embedmetadata":True,
        "merge_output_format":"mp4",
        "progress_hooks": [tqdm_hook],
    }
    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        try:
            ydl.download([video_url])
            print("Download Completed Successfully!")
        except Exception as e:
            print(f"An error occurred during download: {e}")

# ======================================================================================

if "__main__" == __name__:
    try:
        print("Please Enter The Video URL")
        user_video_url=input("=> ") 
        print("Fetching Available Formats... Please Wait.")
        resoultion_dict = get_available_qualities(user_video_url.strip())
        resoultion_dict= clear_empty_data(resoultion_dict)
        numbered_resolutions_dict=print_available_qualities(resoultion_dict)
        print("="*50)
        print("Choose A Quality To Download:")
        wanted_quality = input("=> ").strip()
        download_video(user_video_url,numbered_resolutions_dict[int(wanted_quality)])

    except Exception as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except ValueError:
        print("Invalid input. Please enter a valid number for quality selection.")
    except IndexError:
        print("Selected quality is out of range. Please select a valid quality number.")
            


def shit_show:
    print("'hello")
    





