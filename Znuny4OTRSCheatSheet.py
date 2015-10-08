from os.path import dirname, exists, join, realpath, os
import sublime, sublime_plugin
import string, re, pprint

MY_PLUGIN_DIR = dirname(realpath(__file__))

# Shortcut Command handling as well direct 
# Tools -> CheatSheet Menu Handler for Znuny overviews
class CheatSheetCommand(sublime_plugin.WindowCommand):
  def run(self, **args):

    # Based on Ideas on how to open files from "Cheat Sheet" for Sublime Package Manager

    # Get the filename from the argument passed by the Calling Menu
    # Add the ending
    cheats = [ args["cheatsheet"] + ".png", args["cheatsheet"] + ".jpg", args["cheatsheet"] + ".gif" , args["cheatsheet"] + ".pdf" ]
    userNames = []
    defaultNames = []
    cheat = ''

    # Check if the Chosen File exists first in the UsersCheats
    # if not there check in the Znuny4OTRS-Sublime Package Cheat directory
    # if it doesn't exist 
    for name in cheats:
      userCheat = join(sublime.packages_path(), "User/Znuny4OTRSCheatSheets", name)
      defaultCheat = join(MY_PLUGIN_DIR, "Znuny4OTRSCheatSheets/Sheets", name)

      if exists(userCheat):
        cheat = userCheat
        print("UserCheat %s" % userCheat)
        break
      elif exists(defaultCheat):
        cheat = defaultCheat
        print("DefaultCheat %s" % defaultCheat)
        break
      else:
        return


    # if we found a cheat 
    # open it
    if len(cheat) > 0:
      dest_view = self.window.open_file(cheat)
      def set_view_props():
        if dest_view.is_loading():
          sublime.sublime.set_timeout(set_view_props, 50)
          return

      set_view_props()
      self.dest_view = dest_view

# Search for cheat sheets in the 
# Cheet User and Package Cheet Sheet directory
class CheatSheetSearchCommand(sublime_plugin.WindowCommand):

    # local variables used over more than one function
    # category_names is an array containing just the names of the Categories
    category_names = []

    # category_all contains a dictionary (perl hash)
    # Keys are category names as stored in the category_name array
    # Values are hashes (dictionaries) containing
    # {
    #   File: Filename.png
    #   Path: Path/To/File/
    # }
    category_all = {}

    def run(self, **args):
      # Fillup paths for user and default (e.g. package) directories
      userCheat = join(sublime.packages_path(), "User/Znuny4OTRSCheatSheets/")
      defaultCheat = join(MY_PLUGIN_DIR, "Znuny4OTRSCheatSheets/Sheets")

      self.category_names = []
      category_all = {}

      # Find all files of the default and the user directory
      # this calls the findfiles function you'll see later on
      self.findfiles(defaultCheat)
      self.findfiles(userCheat)

      # If error printing of deeper datastructures is necessary use this construct:
      # pp = pprint.PrettyPrinter(indent=4)
      # pp.pprint(self.category_names)

      # sort the categories in our category_all dictionary (e.g. hash)
      # and assign them sortedly to the category_names array
      # selecting a category returns the index of the category inside this array
      for category in sorted(self.category_all):
        self.category_names.append(category)

      # Now fire up sublimes' search popup populated with the categories stored in category_names
      # on choosing a category self.show_cheat_sheet is called with the index position of the chosen category
      sublime.active_window().show_quick_panel(self.category_names, self.show_cheat_sheet)

    def show_cheat_sheet(self, index):

      # If we don't have a chosen number exit
      if index == -1: return

      # to open files we need the path and filename of our category
      # that's why we use the Category name stored in 
      # category_names[ index ] as key of our category_all dictionary to get the path and the filename and join them to 
      # pathAndFile
      pathAndFile = join( self.category_all[ self.category_names[ index ] ][ 'Path' ], self.category_all[ self.category_names[ index ] ][ 'File' ] )

      # make sure the file is still there before trying to open it
      if os.path.isfile( pathAndFile ):

        # open the file
        dest_view = self.window.open_file(pathAndFile)

        # if it takes a little longer give it some more time 
        def set_view_props():
          if dest_view.is_loading():
            sublime.sublime.set_timeout(set_view_props, 50)
            return

        # now make the newly opened window the default visible one
        set_view_props()
        self.dest_view = dest_view


    # findfiles looks for all png, jpg, gif and pdf files of a given directory
    # and populates the self.category_all dictionary (e.g. hash of hashes)
    def findfiles(self, path):
      # Check if the given path is a directory
      if os.path.isdir(path):

        # get all files of the directory
        files = [name for name in os.listdir(path) if os.path.isfile(join(path, name))]

        for f in files:
          # use a regex to get just those files ending in .png, .jpg, .gif or .pdf
          if re.search(r".*\.(png|jpg|gif|pdf)$",f):

            # populate category_all
            # Sample Datastructure:
            # category_all = {
            #                  Overview: {
            #                       File: 'Overview.png',
            #                       Path: '/Path/To/Sublime Text 3/Packages/Znuny4OTRS-Sublime/Znuny4OTRSCheatSheets/Sheets/'
            #                   },
            #                   Frontend: {
            #                       File: 'Frontend.png',
            #                       Path:  '/Path/To/Sublime Text 3/Packages/Znuny4OTRS-Sublime/Znuny4OTRSCheatSheets/Sheets/'
            #                   }
            #                 }
            self.category_all[f[:-4]] = {"File":f, "Path":path}
