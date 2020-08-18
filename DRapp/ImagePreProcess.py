import os                 # OPERATING SYSTEM MODULE    -   required for Checking Path
import cv2                # OPENCV MODULE              -   required for Image Processing
import numpy as np 
import shutil 

class imgpp():
	def say_hi(self):
		return "hi"


	def check_path(self,image_path):
		if( not ( os.path.exists( image_path ) ) ):
			print( "Sorry!! Image Path doesn't Exists!" )
			return 0
		else:
			return 1

	def resize(self,image_path):
		"""if(not (check_path(image_path))):
									return 0  # Return 0 indicating path doesn't exist!!"""

		try:
			# Read the Image ( Colored )
			img = cv2.imread(image_path)
			print(img.size,img.shape)

			if( img.size != 0 ) :
				# Get a GRAY SCALE Copy of the Original Colored Image
				grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				# Display the GREY Image
				#cv2_imshow(grey)

				# APPLY THRESHOLDING TO GREY IMAGE
				# https://docs.opencv.org/master/d7/d4d/tutorial_py_thresholding.html
				# The Entire image must have only two pixel values, Pixel Values above( >8 = 255 ) and below ( <8 = 0)
				_, th2 = cv2.threshold(grey, 8, 255, cv2.THRESH_BINARY)
				# Display the Thresholded Image
				#cv2_imshow(th2)

				# Contours can be explained simply as a curve joining all the continuous points (along the boundary),
				# having same color or intensity. The contours are a useful tool for shape analysis and object detection and recognition.
				# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.html
				# in cv2.findContours() function,
				# first one is source image,
				# second is contour retrieval mode,
				# third is contour approximation method.
				contours, hierarchy = cv2.findContours(th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

				# Plotting the contours
				#img = cv2.drawContours(img, contours, -1, (0,255,0), 3)
				#cv2_imshow(img)



				# Finding the Area of all the contours
				# https://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html
				areas = [cv2.contourArea(contour) for contour in contours]
				# Get the index of the max Area
				max_index = np.argmax(areas)
				# Copy the Max Area Contour value into cnt
				cnt = contours[max_index]
				#print(areas,max_index,cnt)

				# Find the values of the Bounding Rectangle ( Rectangle that fits the Contour Circle )
				x, y, w, h = cv2.boundingRect(cnt)

				# Ensure bounding rect should be at least 16:9 or taller
				if ( w / h > 16 / 9 ):
					# increase top and bottom margin
					newHeight = w / 16 * 9
					y = y - (newHeight - h) / 2
					h = newHeight

				# Crop with the largest rectangle
				crop = img[int(y):int(y + h), int(x):int(x + w)]
				resized_img = cv2.resize(crop, (256, 256))
				print(resized_img.shape)

				#print("Successfully cropped the Image")
				cv2.imwrite(image_path,resized_img)
				#cv2.imwrite("64*64",resized_img)
				#cv2.imshow(resized_img)
				print("Successfully written the cropped image to the destined path")
				return 1
		except:
			print("Disformed image found")
			return 0


	def final_image(self,image_path):
		image = cv2.imread(image_path)
		print(image.shape)
		image_file_path = image_path.split('/')
		image_file_name = image_file_path.pop()
		image_file_path = "/".join(image_file_path)

		if(image.shape == 256,256,3):
			#Obtaining the green channel Image by Splitting the RGB Image
			blue, green, red = cv2.split(image)
			print("green channel success")
			
			# Creating CLAHE
			clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
			clahe_image = clahe.apply(green)
			print("clahe success")

			# MIN-MAX NORMALIZATION
			normalizedImg = np.zeros((256, 256))
			normalizedImg = cv2.normalize(clahe_image, normalizedImg, 0, 255, cv2.NORM_MINMAX)
			normalized_image_name = image_file_path + "/normalized_" + image_file_name
			print(normalized_image_name)
			#cv2.imshow(normalizedImg)
			cv2.imwrite(normalized_image_name, normalizedImg)

			return 1

		else:
			print("Unexpected Image Shape, Expected (256,256,3) but got",image.shape)
			return 0

	def clean_up():
		for name in dir():
			if not name.startswith('_'):
				del globals()[name]


	def preprocess_automate(self,left_path,right_path):
		obj = imgpp()
		if(obj.check_path(left_path) and obj.check_path(right_path)):
			if(obj.resize(left_path) and obj.resize(right_path)):
				if (obj.final_image(left_path) and obj.final_image(right_path)):
					return(1)
				else:
					return(0)
			else:
				return(0)
		else:
			return(0)