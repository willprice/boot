#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
import os

_content1 = '''
## Nanorc files
include "/usr/share/nano/nanorc.nanorc"

## C/C++
include "/usr/share/nano/c.nanorc"

## Cascading Style Sheets
include "/usr/share/nano/css.nanorc"

## Debian files
include "/usr/share/nano/debian.nanorc"

## Gentoo files
include "/usr/share/nano/gentoo.nanorc"

## HTML
include "/usr/share/nano/html.nanorc"

## PHP
include "/usr/share/nano/php.nanorc"

## TCL
include "/usr/share/nano/tcl.nanorc"

## TeX
include "/usr/share/nano/tex.nanorc"

## Quoted emails (under e.g. mutt)
include "/usr/share/nano/mutt.nanorc"

## Patch files
include "/usr/share/nano/patch.nanorc"

## Manpages
include "/usr/share/nano/man.nanorc"

## Groff
include "/usr/share/nano/groff.nanorc"

## Perl
include "/usr/share/nano/perl.nanorc"

## Python
include "/usr/share/nano/python.nanorc"

## Ruby
include "/usr/share/nano/ruby.nanorc"

## Java
include "/usr/share/nano/java.nanorc"

## AWK
include "/usr/share/nano/awk.nanorc"

## Assembler
include "/usr/share/nano/asm.nanorc"

## Bourne shell scripts
include "/usr/share/nano/sh.nanorc"

## POV-Ray
include "/usr/share/nano/pov.nanorc"

## XML-type files
include "/usr/share/nano/xml.nanorc"

## Custom coloring for VHDL files.
syntax "vhdl" "\.vhdl$"
icolor brightblue "def [0-9A-Z_]+"
color brightred "\<(abs|access|after|alias|all|and|architecture|array|assert|attribute|begin|block|body|buffer|bus|case|component|configuration|constant|disconnect|downto|else|elsif|end|entity|exit|file|for|function|generate|generic|group|guarded|if|impure|in|inertial|inout|is|label|library|linkage|literal|loop|map|mod|nand|new|next|nor|not|null|of|on|open|or|others|out|package|port|postponed|procedure|process|pure|range|record|register|reject|rem|report|return|rol|ror|select|severity|signal|shared|sla|sll|sra|srl|subtype|then|to|transport|type|unaffected|units|until|use|variable|wait|when|while|with|xnor|xor)\>"
color green "\<(std_logic|std_logic_vector|bit)\>"
color magenta "\<(ieee|std_logic_1164|numeric_std|numeric_signed|numberic_unsigned|numeric_bit|math_real|math_complex|std_logic_arith|std_logic_unsigned|std_logic_signed)\>"
color brightgreen "['][^']*[^\\][']" "[']{3}.*[^\\][']{3}"
color brightgreen "["][^"]*[^\\]["]" "["]{3}.*[^\\]["]{3}"
color blue "--.*$"

# set tab to spaces of size 4 spaces
set tabstospaces
set tabsize 4

# enable mouse
set mouse

# use one additional line
set morespace

#set the line number indication in the status bar
#set const

# set autoindentation
set autoindent

'''

def make():
    ''' Create a nano configuration file named ".nanorc" in ~/
        IMPORTANT: if you already have this file NOTHING WILL BE DONE. 
    '''
    if os.path.isfile(os.getenv("HOME")+'/.nanorc'):
        print 'WARNING. "~/.nanorc" file already exist. Nothing will be done.'
    else:
        with open(os.getenv("HOME")+'/.nanorc','w') as fl:
            fl.write(_content1)
        print '"~/.nanorc" configuration file created.' 
    return 0


