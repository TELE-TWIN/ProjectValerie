

class Wrapper():
	
	service = "OpenSubtitles"
	
	def __init__(self):
		self.year = "2005"
		self.season = ""
		self.episode = ""
		self.tvshow = ""
		self.title = "An Inconvenient Truth"
		
		self.language_1 = "English"
		self.language_2 = "German"
		self.language_3 = "None"
		
		#self.file_original_path = "Transporter.2.2005.UNCUT.720p.BluRay.DTS.x264-CtrlHD.mkv"
		self.file_original_path = "/mnt/nfs/Movies/An.Inconvenient.Truth.HDTV.720p.AC3.2.0.x264-DiR.mkv"
		self.set_temp = False
		self.rar = False
		return
		self.year = ""
		self.season = "3"
		self.episode = "18"
		self.tvshow = "30 Rock"
		self.title = "30 Rock"
		self.file_original_path = "/mnt/nfs/TVShows/30 Rock/30.Rock.S03E18.720p.HDTV.X264-DIMENSION.mkv"
	
	def Search_Subtitles( self ):
		exec ( "from services.%s import service as Service" % (self.service))
		self.Service = Service
		
		print "searching sub for", self.file_original_path
		self.subtitles_list, self.session_id, msg = self.Service.search_subtitles( self.file_original_path, self.title, self.tvshow, self.year, self.season, self.episode, self.set_temp, self.rar, self.language_1, self.language_2, self.language_3 )
		
		
		# Checking for direct match
		for subtitle in self.subtitles_list:
			try:
				print subtitle
				#print "filename:", subtitle["filename"]
			except:
				pass
		#print "self.subtitles_list:", self.subtitles_list
		print "self.session_id:", self.session_id
		print "msg:", msg
		
		

if ( __name__ == "__main__" ):
	Wrapper().Search_Subtitles()