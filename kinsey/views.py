from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

from .forms import ImportFileForm
from .myfunc import Initializer, Resume, NewScrape, Progress
from .stock_checker import Scraper
from .thread_sample import TestThreading
import csv
import io
from collections import OrderedDict
import pandas as pd
import json
import os
import threading
import time



# Create your views here.

def decode_utf8(input_iterator):
	for l in input_iterator:
		yield l.decode('utf-8')


def handle_file(f):
	reader = csv.DictReader(decode_utf8(f))
	for_pd = []
	for row in reader:
		for_pd.append(dict(row))

	df = pd.DataFrame(for_pd)
	print(df)


def deleteexcel():

	for f in os.listdir('media/from_chino'):
		if os.path.isfile(os.path.join('media/from_chino', f)):
			os.unlink(os.path.join('media/from_chino', f))

	for f in os.listdir('media/to_chino'):
		if os.path.isfile(os.path.join('media/to_chino', f)):
			os.unlink(os.path.join('media/to_chino', f))


def home(request):

	# stock_checker.main()
	# check = Initializer()
	# if check.resume:
	# 	r_value = check.return_val
	# 	return redirect('resume')

	p = Progress()
	status = {'existing': False}
	if p.has_existing:
		percnt = (p.completed / p.target) * 100
		status = dict(existing=p.has_existing, percnt=round(percnt, 2), excel=p.xl_file, completed=p.completed, target=p.target)

	form = ImportFileForm
	if request.method == 'POST':
		deleteexcel()
		f = request.FILES['file']
		print(f.name, f)
		fs = FileSystemStorage()
		filename = fs.save("from_chino/"+f.name, f)
		uploaded_file_url = fs.url(filename)
		print(uploaded_file_url)
		return redirect('resume')

	else:
		form = ImportFileForm()

	return render(request, 'home.html', context={'form': form, 'status': status})


def resume(request):

	jscheck = open('media/status.json','r', encoding='utf-8')
	jsobject = json.load(jscheck)[0]
	jscheck.close()

	res = Resume()
	file = res.return_val['file']
	context = {'file': file}
	sourcefile = context['file'].replace(".xlsx", "")

	if not jsobject['running']:
		myscraper = Scraper(sourcefile=sourcefile)
		print("From my Scraper ----> ", myscraper.filename)
		return render(request, 'resume.html', context=context)
	else:
		print("Just redirect to resume page")
		return render(request, 'resume.html', context=context)


def cancelled(request):
	try:
		referer = request.META['HTTP_REFERER']
		referer = referer[referer.rfind('/')+1:]
	except Exception as e:
		referer = ""

	if referer == 'resume':  # MAKE SURE REQUEST FORM RESUME PAGE
		time.sleep(2)
		jscheck = open('media/status.json','r', encoding='utf-8')
		jsobject = json.load(jscheck)[0]
		jscheck.close()

		js = open('media/status.json', 'w', encoding='utf-8')
		json.dump([{'running': False, 'excel_saved': False}], js, indent=3)
		js.close()
		time.sleep(1)
		#
		# while True:
		# 	js = open('media/status.json')
		# 	status = json.load(js)[0]
		# 	js.close()
		# 	if status['excel_saved']:
		# 		break
		# 	time.sleep(.5)
		# 	print('Please wait....')
		return render(request, 'cancelled.html', context={'file': os.listdir('media/from_chino')[0]})
	else:
		return redirect('resume')


def progress(request):
	res = Resume()
	file = res.return_val['file']
	context = {'file': file}
	sourcefile = context['file'].replace(".xlsx", "")

	try:
		# scraping progess
		fopen = open('media/to_chino/progress-{}.json'.format(sourcefile))
		ffile = json.load(fopen)
		fopen.close()
	except Exception as e:
		ffile = dict(completed=0, total=0)

	# scraper state
	fs = open('media/status.json')
	fstatus = json.load(fs)[0]
	ffile.update({'running': fstatus['running']})
	fs.close()

	return HttpResponse(json.dumps(ffile), content_type='application/json')







