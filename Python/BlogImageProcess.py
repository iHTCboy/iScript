#coding: utf-8
from PIL import Image
import os
import sys
import json
from datetime import datetime
from ImageProcess import Graphics

Image.MAX_IMAGE_PIXELS = 100000000 #提高触发DecompressionBombWarning警告的阈值

# 定义压缩比，数值越大，压缩越小
SIZE_normal = 1.0
SIZE_small = 1.5
SIZE_more_small = 2.0
SIZE_more_small_small = 3.0

## 图片路径
origin_path = '/Users/HTC/Documents/Personal/P-Project/OneMindMap/MindMapImages/'
thumbnail_path = '/Users/HTC/Documents/Personal/P-Project/OneMindMap/Thumbnail/'
json_path = '/Users/HTC/Documents/Personal/P-Project/iHTCBlog/source/more/onemindmap.json'

#origin_path = '/Users/HTC/Documents/Personal/P-Project/iGallery/Backup/Origin/'
#thumbnail_path = '/Users/HTC/Documents/Personal/P-Project/iGallery/Backup/Thumbnail/'
#json_path = '/Users/HTC/Documents/Personal/P-Project/iHTCBlog/source/more/photos.json'


def make_directory(directory):
	"""创建目录"""
	os.makedirs(directory)

def directory_exists(directory):
	"""判断目录是否存在"""
	if os.path.exists(directory):
		return True
	else:
		return False

def list_img_file(directory):
	"""列出目录下所有文件，并筛选出图片文件列表返回"""
	old_list = os.listdir(directory)
	# print old_list
	new_list = []
	for filename in old_list:
		fileformat = filename.split(".")
		if fileformat[-1].lower() == "jpg" or fileformat[-1].lower() == "jpeg" or fileformat[-1].lower() == "png" or fileformat[-1].lower() == "gif":
			new_list.append(filename)
	# print new_list
	return new_list


def print_help():
	print("""
	This program helps compress many image files
	you can choose which scale you want to compress your img(jpg/png/etc)
	1) normal compress(4M to 1M around)
	2) small compress(4M to 500K around)
	3) smaller compress(4M to 300K around)
	""")

def compress(choose, des_dir, src_dir, file_list):
	"""压缩算法，img.thumbnail对图片进行压缩，
	
	参数
	-----------
	choose: str
			选择压缩的比例，有4个选项，越大压缩后的图片越小
	"""
	if choose == '1':
		scale = SIZE_normal
	if choose == '2':
		scale = SIZE_small
	if choose == '3':
		scale = SIZE_more_small
	if choose == '4':
		scale = SIZE_more_small_small
	for infile in file_list:
		img = Image.open(src_dir+infile)
		# size_of_file = os.path.getsize(infile)
		# 不能大于500x500
		w, h = img.size
		if w> 500 or h > 500:
			w = 500 if (w > 500) else int(w)
			h = 500 if (h > 500) else int(h)
			img.thumbnail((w, h))
			img.save(des_dir + infile)
		
def compress_photo():
	'''调用压缩图片的函数
	'''
	src_dir, des_dir = thumbnail_path, thumbnail_path
	
	if directory_exists(src_dir):
		if not directory_exists(src_dir):
			make_directory(src_dir)
		# business logic
		file_list_src = list_img_file(src_dir)
	if directory_exists(des_dir):
		if not directory_exists(des_dir):
			make_directory(des_dir)
		file_list_des = list_img_file(des_dir)
		# print file_list
#	'''如果已经压缩了，就不再压缩'''
#	for i in range(len(file_list_des)):
#		if file_list_des[i] in file_list_src:
#			file_list_src.remove(file_list_des[i])
#	if len(file_list_src) == 0:
#		print("=====没有新文件需要压缩=======")
	compress('3', des_dir, src_dir, file_list_src)

def handle_photo():
	'''根据图片的文件名处理成需要的json格式的数据
	
	-----------
	最后将data.json文件存到博客的source/photos文件夹下
	'''
	src_dir = origin_path
	file_list = list_img_file(src_dir)
	list_info = []
#	file_list.sort(key=lambda x: x.split('_')[0])   # 按照日期排序
	file_list.sort()   # 按照日期排序
	for i in range(len(file_list)):
		filename = file_list[i]
		datas = filename.split("_")
		formats = filename.split(".")
		info = filename.replace(datas[0]+'_', '').replace('.'+formats[-1], '')
		if not str.isdigit(datas[0]):
			datas = filename.split("-")
			info = filename.replace(datas[0]+'-', '').replace('.'+formats[-1], '')
			if not str.isdigit(datas[0]):
				print('[Error]: 图片名字格式不正确！')
				return
		
		img = Image.open(src_dir+filename)
		(x, y) = img.size 
		size = str(x) + 'x' + str(y)
				
		date_str = datas[0][:6]            
		date = datetime.strptime(date_str, "%Y%m")
		year_month = date_str[0:7] 
		if i == 0:  # 处理第一个文件
			new_dict = {"date": year_month, "arr":{'year': date.year,
																   'month': date.month,
																   'link': [filename],
																   'text': [info],
																   'size': [size],
#																   'type': ['image']
																   }
										} 
			list_info.append(new_dict)
		elif year_month != list_info[-1]['date']:  # 不是最后的一个日期，就新建一个dict
			new_dict = {"date": year_month, "arr":{'year': date.year,
												   'month': date.month,
												   'link': [filename],
												   'text': [info],
												   'size': [size],
#												   'type': ['image']
												   }
						}
			list_info.append(new_dict)
		else:  # 同一个日期
			list_info[-1]['arr']['link'].append(filename)
			list_info[-1]['arr']['text'].append(info)
			list_info[-1]['arr']['size'].append(size)
#			list_info[-1]['arr']['type'].append('image')
	
	# 从时间长倒序
	for info in list_info:
		arr = info['arr']
		arr['link'].reverse()
		arr['text'].reverse()
		arr['size'].reverse()
		

	list_info.reverse()  # 翻转
	final_dict = {"list": list_info}
	with open(json_path, "w") as fp:
		json.dump(final_dict, fp)
	
	print('[Success] save json file.')

def cut_photo():
	"""裁剪算法
	
	----------
	调用Graphics类中的裁剪算法，将src_dir目录下的文件进行裁剪（裁剪成正方形）
	"""
	src_dir = origin_path
	out_dir = thumbnail_path
	if directory_exists(src_dir):
		if not directory_exists(src_dir):
			make_directory(src_dir)
		# business logic
		file_list = list_img_file(src_dir)
		# print file_list
		if file_list:
			cut_list = []
			print_help()
			for infile in file_list:
				#img = Image.open(src_dir+infile)
				outfile = out_dir + infile
				if directory_exists(outfile):
					print('skipe image')
					continue
				
				cut_list.append(infile)
				Graphics(infile=src_dir+infile, outfile=out_dir + infile).cut_by_ratio()
				
			print('cut images:' + str(cut_list))
		else:
			pass
	else:
		print("source directory not exist!")     



def git_operation():
	'''
	git 命令行函数，将仓库提交
	
	----------
	需要安装git命令行工具，并且添加到环境变量中
	'''
	os.system('cd "{}"; cd ..; git add --all; git commit -m "update photos"; git push origin master;'.format(origin_path))
#	os.system('cd ..')
#	os.system('git add .')
#	os.system('git commit -m "update photos"')
#	os.system('git push origin master')


if __name__ == "__main__":
	cut_photo()        # 裁剪图片，裁剪成正方形，去中间部分
	compress_photo()   # 压缩图片，并保存到mini_photos文件夹下
	git_operation()    # 提交到github仓库
	handle_photo()     # 将文件处理成json格式，存到博客仓库中
	