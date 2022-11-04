from random			import randint as randInt,choices as randChoice
from string			import ascii_letters,digits,punctuation
from win32api		import SetConsoleTitle as title
from os				import system as run,path
from time			import perf_counter
from playsound		import playsound
from fpstimer		import FPSTimer
import cv2 as cv

vidName =	"video.mp4"
audName =	"audio.mp3"

vid =	cv.VideoCapture(vidName)

assert vid.isOpened(),"failed to open "+vidName
assert path.isfile(audName),"audio file not found"

vidWidth:int =		int(vid.get(cv.CAP_PROP_FRAME_WIDTH))
vidHeight:int =		int(vid.get(cv.CAP_PROP_FRAME_HEIGHT))
vidFrameCount:int =	int(vid.get(cv.CAP_PROP_FRAME_COUNT))
vidFPS:float =		vid.get(cv.CAP_PROP_FPS)

class ascii:
	width:int =				vidWidth//4
	height:int =			vidHeight//6	# smaller than the width to not make it look stretched in the console
	chars:tuple[str,...] =	(" ",".","°","*","o","O","#","@")[::1]
	frames:list[str] =		[]

run("cls && color 0f")	# clear console and make the white text brighter

rhetoricFunniness =			lambda:"".join(randChoice(ascii_letters+digits+punctuation,k=randInt(1,4))).center(4)
renderStartTime:float =		perf_counter()

while 1:
	notError,frame = vid.read()
	if notError:
		doneFrames = len(ascii.frames)
		curFrameNum = doneFrames+1
		# https://stackoverflow.com/a/473376											avoiding zero division error
		renderETCtime = ((perf_counter() - renderStartTime) * (vidFrameCount - doneFrames)) / (doneFrames or 1) 
		title(f"({round(curFrameNum/vidFrameCount * 100)}%) {curFrameNum}/{vidFrameCount} (ETC: {renderETCtime:.2f} seconds)")
		print(f"\r[{rhetoricFunniness()}] Rendering [{rhetoricFunniness()}]",end="")
		frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
		frame = cv.resize(frame,(ascii.width,ascii.height))
		# https://wikipedia.org/wiki/ANSI_escape_code#CSI_(Control_Sequence_Introducer)_sequences
		#					vvvvvvvvvvvv
		ascii.frames.append("\x1b[1;1H" + "\n".join(
			map(
				lambda line:"".join(
						map(
							# when the frame is converted to grayscale beforehand, then each pixel is a number 0-255 instead of a regular RGB/BGR ndarray
							# reason for doing int(pixel) is because pixel is a numpy.uint8 which needs to be a regular int for our purposes
							lambda pixel:ascii.chars[round(max(int(pixel)/255 * len(ascii.chars) - 1,0))],
							line
						)
					),
				frame
			)
		))
	else:break

timer = FPSTimer(vidFPS)
min,sec = divmod(vidFrameCount//round(vidFPS),60) # https://stackoverflow.com/a/775075

playsound(audName,False)
for index,asciiFrame in enumerate(ascii.frames,start=1):
	if index % 10 == 0:run(f"mode CON: cols={ascii.width} lines={ascii.height}")
	remMin,remSec = divmod(index//round(vidFPS),60)
	title(f"({remMin}:{remSec:02}/{min}:{sec:02}) {index}/{vidFrameCount}")
	print(asciiFrame,end="")
	timer.sleep()