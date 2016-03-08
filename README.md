![Znuny logo](http://znuny.com/assets/logo_small.png)

Sublime
===============
Znuny4OTRS is a Sublime Text 2/3 plugin that helps you to make OTRS development less painful.

### Feature List

* Automatic fetching of framework files from github.
* Automatic quoting with custom markers via keyboard shortcut.
* Automatic 'Frontend::Template::GenerateBlockHooks' config XML generation from .tt template file.
* Automatic creation of the ObjectDependencies array.
* Add folder from workspace to project.
* OTRS code snippts for fast, consistent and error free coding.

### Installation

To install this plugin, you have three options:

1. If you have [Sublime Package Control](http://wbond.net/sublime_packages/package_control) installed, simply search for `Znuny4OTRS` to install.
2. Clone source code to Sublime Text packages folder *Sublime Text 2/Packages* or *Sublime Text 3/Packages*.
3. Download archive with the latest [release](https://github.com/znuny/Znuny4OTRS/releases) and unpack it to Sublime Text packages folder *Sublime Text 2/Packages* or *Sublime Text 3/Packages*.

*OSX*

    cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
    - or ST 3 -
    cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/
    git clone git://github.com/znuny/Znuny4OTRS-Sublime.git

*Linux*

    cd ~/.config/sublime-text-2/Packages
    - or ST 3 -
    cd ~/.config/sublime-text-3/Packages
    git clone git://github.com/znuny/Znuny4OTRS-Sublime.git

*Windows*

    cd "%APPDATA%\Sublime Text 2\Packages"
    - or ST 3 -
    cd "%APPDATA%\Sublime Text 3\Packages"
    git clone git://github.com/znuny/Znuny4OTRS-Sublime.git

### Usage

#### otrs code templates

```otrs``` + Sublime Text autocomplete (command ```auto_complete```)

#### Frontend::Template::GenerateBlockHooks config XML generation

Default keyboard shortcut: ```strg+alt+z, h```

<img src="https://cloud.githubusercontent.com/assets/3873515/7705818/db4f3510-fe46-11e4-90b9-09093b063ac0.gif" width="640">

#### Automatic custom marker quoting

Default keyboard shortcut: ```strg+alt+z, q```

Works with active Perl, JavaScript and HTML sytax.

<img src="https://cloud.githubusercontent.com/assets/3873515/7766583/d64a68fc-006a-11e5-8d9c-682ba128297a.gif" width="640">

#### Automatic creation of the ObjectDependencies array

Default keyboard shortcut: ```strg+alt+z, d```

Inserts the @ObjectDependencies array by parsing the file content. Only regular used OM calls are supported.

<img src="https://cloud.githubusercontent.com/assets/3873515/9132331/0ec230a6-3cf3-11e5-8421-9261d25d2694.gif" width="640">

#### Add folder from workspace(s) to project

Default keyboard shortcut: ```strg+alt+z, p```

Provides a searchable list of folders that can be added to the project. All folders of configurable workspace folders will be displayed.

Preferences -> Package Settings -> Znuny4OTRS -> Settings -> "znuny4otrs_workspaces"

<img src="https://cloud.githubusercontent.com/assets/3873515/9403960/a7b9d0d6-47eb-11e5-93a7-d7c513c57ad5.gif" width="640">

#### Fetching OTRS files from github

Default keyboard shortcut: ```strg+alt+z, c```

Opens a project, branch and file selection list to chose a framework or addon file from. The file will get fetched live from the selected github branch and added to the (selected) folder. The Znuny copyright and the origin tag will be added automatically to the file header for you. The file will also be automatically added to the 'Custom/' directory in case it's a file with one of the file extensions '.pm', '.dtl' or '.tt'.

The github API is limited to 60 requests per hour for non authorized requests. Yo can provide your github username and an access token to push this limit to 5000 requests per hour. Please see the [official github doc](https://developer.github.com/v3/#rate-limiting) for further information.
You can generate the access token in your [github settings](https://github.com/settings/tokens).

To add your access credentials go to:
Preferences -> Package Settings -> Znuny4OTRS -> Settings

And add the settings "znuny4otrs_github_username" and "znuny4otrs_github_token" accordingly.

<img src="https://cloud.githubusercontent.com/assets/3873515/11466357/a218c11a-9740-11e5-9e9b-2f0e07e60b1b.gif" width="640">

#### Creating SOPM Filelist from project

Default keyboard shortcut: ```strg+alt+z, f```

Inserts the SOPM Filelist content containing all files of a selectable project.

<img src="https://cloud.githubusercontent.com/assets/3873515/13220468/a1cdd8ee-d976-11e5-8b69-cf936c63c76e.gif" width="640">

### Commercial Support

For this extension and for OTRS in general visit [http://znuny.com](http://znuny.com). Looking forward to hear from you!

Enjoy!

 Your Znuny Team!

 [http://znuny.com](http://znuny.com)
