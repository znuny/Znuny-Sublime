![Znuny logo](http://znuny.com/assets/logo_small.png)

Sublime
===============
Znuny4OTRS is a Sublime Text 2/3 plugin that helps you to make OTRS development less painful.

### Feature List

* Automatic quoting with custom markers via keyboard shortcut.
* Automatic 'Frontend::Template::GenerateBlockHooks' config XML generation from .tt template file.
* Automatic creation of the ObjectDependencies array.
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

### Commercial Support

For this extension and for OTRS in general visit [http://znuny.com](http://znuny.com). Looking forward to hear from you!

Enjoy!

 Your Znuny Team!

 [http://znuny.com](http://znuny.com)
