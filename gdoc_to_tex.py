import csv
import re
import requests as req

DOC_ID = # REDACTED
TAB_ID = # REDACTED
FILE_NAME = 'chapters/words.tex'

# spreadsheet format
# WORD | PRONUNCIATION | PART OF SPEECH | DEFINITION | EXAMPLE | ETYMOLOGY | OFFICIAL? | ORIGIN

# definition format
# (notes) meaning: _example_ "translated"

def to_latex(row):
    lemma, sound, pos, senses, etym, incl, source = row
    if incl == 'TRUE':
        extra = build_extra(sound, pos, etym)
        defn = build_defn([s.strip() for s in senses.split(';')])
        return format(f'\\entry[{extra}]{{{lemma}}}{{{defn}}}')

def build_extra(sound, pos, etym):
    extra = f'pos={pos}' # assumes pos is never blank
    if sound:
        extra += f',sound={sound}'
    if etym:
        extra += f',etym={etym}'
    return extra

def build_defn(senses):
    defn = ''
    for sense in senses:
        note, gist, ex = '', '', ''
        parts = [s.strip() for s in re.split(r'(\([^)]*\))|:(.*)', sense) if s]
        if len(parts) == 3:  # has note, meaning, and example
            note, gist, ex = parts
        if len(parts) == 2:
            if sense.find(':') != -1:  # has only meaning and example
                gist, ex = parts
            else:  # has only meaning and note
                note, gist = parts
        if len(parts) == 1:  # has only meaning
            gist = sense
        note = re.sub(r'[\(\)]', '', note)
        defn += build_sense(note, gist, ex) + ' '
    return defn

def build_sense(note, gist, ex):
    sense = '\\sense'
    if note:
        sense += f'[{note}]'
    sense += f' {gist}'
    if ex:
        sense += f': {ex}'
    return sense

def format(str):
    # regex to turn _abc_ into \rz{abc}
    str = re.sub(r'_([^_]*)_', r'\\rz{\1}', str)
    # regex to turn "abc" into “abc”
    str = re.sub(r'"([^"]*)"', r'“\1”', str)
    # regex to turn @abc.png into image
    str = re.sub(r'@([^ ]*) ', r'\\includegraphics[width=\\columnwidth]{\1} ', str)
    return str

gdoc = req.get('https://docs.google.com/spreadsheets/d/' + DOC_ID + '/export?format=csv&gid=' + TAB_ID).content.decode('utf-8').split('\r\n')[1:] # file without header
gdoc = sorted(gdoc, key=lambda row: ['aąáą́bcdeęéę́fghiíjklmnoǫóǫǫ́pqrstuúvwxyz'.index(c) for c in row.split(',')[0]]) # sort alphabetically
doc = csv.reader(gdoc, delimiter=',', quotechar='\"')
with open(FILE_NAME, 'w') as tex:
    tex.write('\pagelayout{wide}\n\\setlength{\columnsep}{30pt}\n\\begin{multicols}{2}\n')
    section = ''
    for row in doc:
        entry = to_latex(row)
        if entry:
            first = row[0][0].upper()
            if section != first:
                section = first
                tex.write(f'\n\\addsec{{{section}}}\n')
            tex.write(f'{entry}\n')
    tex.write('\n\\end{multicols}')