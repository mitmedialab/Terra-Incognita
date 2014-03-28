from goose import Goose

def extract_image(url):
	print Goose().extract(url).top_image.src


print extract_image('http://www.libyaherald.com/2014/03/23/ahly-benghazi-a-new-caf-champion-in-the-making/#axzz2wwOJBuRT')




