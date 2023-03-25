# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Record frames from the camera and save them to as PNG files.
"""
from time import time, sleep
import sys
from sys import exit, stdout
from os import mkdir, path
import errno
from PIL import Image
from camera import Camera
import pygame



def main(argv):
    if len(argv) < 2:
        print("""Usage: record.py DIRECTORY FRAMES [NAMEOFFSET] [video]
Record FRAMES frames from the camera save them in DIRECTORY
Your Input: %s""" % argv)
        exit(1)
    name = argv[0]
    frames = int(argv[1])
    
    nameOffset = ""
    video = False
    if len(argv) == 3:
    	if not(argv[2] == "video"):
    		nameOffset = argv[2]
    		print("nameoffset recognized: %s" % nameOffset)
	else:
		video = True
    elif len(argv) == 4:
    	nameOffset = argv[3]
    	print("nameoffset recognized: %s" % nameOffset)
    	if argv[2] == "video":
		video = True
    # Initialize the camera and record video frames for a few seconds
    # We select a random exposure for each frame to generate a wide range
    # of lighting samples for training
    camera = Camera(training_mode=True, res=(128, 128))
    record(camera, name, frames, nameOffset, output=video)


def status(text):
    """Helper function to show status updates"""
    stdout.write('\r%s' % text)
    stdout.flush()


def record(camera, dirname, totalFrames, nameOffset, output=False):
    """ Record from the camera """
    
    try:
        mkdir(dirname)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise err
            
    WIDTH = HEIGHT = screen = fontClass = 0
    if output:
    	WIDTH = 320
    	HEIGHT = 240
    	pygame.display.init()
    	pygame.font.init()
    	pygame.display.set_caption("PiCamera record")
    	screen = pygame.display.set_mode((WIDTH, HEIGHT))
    	fontClass = pygame.font.Font('./../Roboto/Roboto-Bold.ttf', 12)
    	fontClass = fontClass.render("straight:shoulder here, head at top edge", True, (255,255,255))

    delay = 3 # Give people a 3 second warning to get ready
    started = time()
    while time() - started < delay:
        status("Recording in %.0f..." % max(0, delay - (time() - started)))
        if output:
        	frame = camera.next_frame_less_iso()
        	surface = pygame.surfarray.make_surface(frame)
        	surface = pygame.transform.rotate(surface, 270)
        	pygame.draw.line(surface, (255,0,0), (0, HEIGHT/3.5), (WIDTH, HEIGHT/3.5), 5)
        	screen.blit(pygame.transform.scale(surface, (WIDTH, HEIGHT)), (0, 0))
        	screen.blit(fontClass, (WIDTH/3.5, HEIGHT/2))
        	pygame.display.flip()
        sleep(0.1)
        


    num_frames = 0
    while num_frames < totalFrames:
        frame = camera.next_frame_less_iso()
        if output:
            surface = pygame.surfarray.make_surface(frame)
            surface = pygame.transform.rotate(surface, 270)
            pygame.draw.line(surface, (255,0,0), (0, HEIGHT/3.5), (WIDTH, HEIGHT/3.5), 5)
            screen.blit(pygame.transform.scale(surface, (WIDTH, HEIGHT)), (0, 0))
            screen.blit(fontClass, (WIDTH/3.5, HEIGHT/2))
            pygame.display.flip()
        image = Image.fromarray(frame)
        filename = (path.join(dirname, nameOffset + '%05d.png') % num_frames)
        image.save(filename, "PNG")
        num_frames += 1

        # Update our progress
        status("Recording [ %d frames]" % (num_frames))

    print('')

    # Save the frames to a file, appending if one already exists
    print('Wrote %d frames to %s\n' % (num_frames, dirname))
    pygame.quit()
        
    


if __name__ == '__main__':
    main(sys.argv[1:])
