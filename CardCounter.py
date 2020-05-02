import cv2
import os
import tbapy
import youtube_dl

tba = tbapy.TBA(os.getenv("TBA_KEY"))

# Map resolution values to YT itag stream codes
QUALITY = {'1080p': '136',
           '720p': '136',
           '480p': '135',
           '360p': '134',
           '144p': '160'}

# BGR color values for cards
YELLOW = {'text': 'yellow', 'value': [93, 254, 249]}
RED = {'text': 'red', 'value': [96, 96, 251]}

# Pixel coordinates are currently hard coded for 360p.
# Left and right station lists are ordered such that they map onto the TBA alliance team ordering
LEFT_STATIONS = [(89, 522), (112, 522), (135, 522)]
LEFT_ELIMS = {'color': 'blue', 'pixel': (0, 0)}

RIGHT_STATIONS = [(89, 151), (112, 151), (135, 151)]
RIGHT_ELIMS = (0, 0)

QUALS_STATIONS = [LEFT_STATIONS, RIGHT_STATIONS]

# Blue check is used to determine which half of the screen is being used for blue.
BLUE_CHECK = (270, 70)
BLUE = [182, 115, 29]


def download_match_video(frc_match, path='Z:/', qual='360p', channel='FIRSTRoboticsCompetition'):
    out_path = path + frc_match['key'] + '.mp4'

    for match_vid in frc_match.videos:
        vid_id = match_vid['key']
        vid_url = 'https://www.youtube.com/watch?v=' + vid_id

        yt_dl_opts = {'outtmpl': out_path,
                      'format': QUALITY[qual]}

        # Check if the uploader is the correct channel to exclude random stands videos before downloading.
        # Break after downloading an official video to avoid duplication in cases where there are multiple official vids
        with youtube_dl.YoutubeDL(yt_dl_opts) as yt_dl:
            info_dict = yt_dl.extract_info(vid_url, download=False)

            if info_dict['uploader'] == channel:
                yt_dl.download([vid_url])
                break
    return out_path


def close_color(color_a=None, color_b=None, tolerance=10):
    close = True

    for i in range(0, 3):
        close = close and abs(color_a[i] - color_b[i]) < tolerance

    return close


def check_for_cards(vid_name, mat):
    card_list = []

    if not os.path.isfile(vid_name):
        print("Missing Match video!")
        return card_list
    else:
        cap = cv2.VideoCapture(vid_name)

        # This sets the current position in the video to the last 20% to try and improve run time slightly
        vid_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, vid_length - round(0.2 * vid_length))

        found_card = False
        img = None

        while cap.isOpened():
            err, img = cap.read()

            # Iterate over card colors and possible stations
            for color in [YELLOW, RED]:
                for side in QUALS_STATIONS:
                    for station, pixel in enumerate(side):
                        if close_color(img[pixel], color['value']):
                            found_card = True
                            print("Team", mat['alliances'][color]['team_keys'][station], 'got a', color['text'], 'card!')

            # Don't need to continue processing video after a valid frame is found
            if found_card:
                break

            # Handle no card found
            if cap.get(cv2.CAP_PROP_POS_FRAMES) >= cap.get(cv2.CAP_PROP_FRAME_COUNT):
                print("No card frame found.")
                break

        while True and found_card:
            cv2.imshow("Card Frame", img)
            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


match = tba.match('2019ohcl_qm13')
vid = download_match_video(match)
check_for_cards(vid, match)
