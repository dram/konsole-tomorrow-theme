#!/usr/bin/env python

import re
import glob
import StringIO

class ColorScheme(dict):
    @classmethod
    def from_xresource(cls, name, fname):
        colors = cls()
        colors.name = name

        macros = {}
        for line in open(fname):
            m = re.match(r'#define\s+(\w+)\s+(#\w+)', line)
            if m:
                macros[m.group(1)] = m.group(2)
                continue

            m = re.match(r'\*\.(\w+):\s+(#?\w+)', line)
            if m:
                color = m.group(2)
                if color in macros:
                    color = macros[color]
                colors[m.group(1).lower()] = color

        return colors

    def rgb_values(self, hex):
        rh, gh, bh = hex[1:3], hex[3:5], hex[5:7]
        return [int(rh, 16), int(gh, 16), int(bh, 16)]

    def to_konsole(self):
        colors = {}
        for name, color in self.items():
            if name == 'cursorcolor':
                continue

            if name.startswith('color') and (len(name) == 7 or name[5] > '7'):
                num = int(name[5:]) - 8
                name = 'Color%dIntense' % num
            else:
                name = name[0].upper() + name[1:]
            colors[name] = color

        out = StringIO.StringIO()
        for name in sorted(colors.keys()):
            print >>out, "[%s]" % name
            print >>out, "Color={},{},{}".format(*self.rgb_values(colors[name]))
            print >>out

        print >>out, "[General]"
        print >>out, "Description={}".format(self.name)

        return out.getvalue()


def main():
    for fname in glob.glob('Xresource*'):
        scheme = ColorScheme.from_xresource(fname[len("Xresource"):], fname)
        open("{}.colorscheme".format(scheme.name),
             'w+').write(scheme.to_konsole())

if __name__ == '__main__':
    main()
