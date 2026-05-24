"""Map plain text characters to Unicode characters simulating various formats.

Tests for this module rely on naming conventions. Each mapping dictionary must be
named with the format <FORMAT>_MAP, where <FORMAT> is the name of the format (e.g.,
ITALIC, BOLD, etc.). The NORMAL_MAP is a special case that maps formatted characters
back to their normal ASCII counterparts. Each mapping dictionary must have a
`to_<format>` function defined, which uses the mapping to convert text to the
specified format.

ITALIC_MAP    ->   to_italic(text)

Underlined characters are graphemes and will be handled correctly. Other graphemes in
your text should be ignored.

There are more formats here than what markdown can express.

:author: Shay Hill
:created: 2026-05-12
"""

import functools as ft

import regex

# fmt: off
ITALIC_MAP = {
    "A": "𝐴", "B": "𝐵", "C": "𝐶", "D": "𝐷", "E": "𝐸", "F": "𝐹", "G": "𝐺", "H": "𝐻",
    "I": "𝐼", "J": "𝐽", "K": "𝐾", "L": "𝐿", "M": "𝑀", "N": "𝑁", "O": "𝑂", "P": "𝑃",
    "Q": "𝑄", "R": "𝑅", "S": "𝑆", "T": "𝑇", "U": "𝑈", "V": "𝑉", "W": "𝑊", "X": "𝑋",
    "Y": "𝑌", "Z": "𝑍",
    "a": "𝑎", "b": "𝑏", "c": "𝑐", "d": "𝑑", "e": "𝑒", "f": "𝑓", "g": "𝑔", "h": "ℎ",
    "i": "𝑖", "j": "𝑗", "k": "𝑘", "l": "𝑙", "m": "𝑚", "n": "𝑛", "o": "𝑜", "p": "𝑝",
    "q": "𝑞", "r": "𝑟", "s": "𝑠", "t": "𝑡", "u": "𝑢", "v": "𝑣", "w": "𝑤", "x": "𝑥",
    "y": "𝑦", "z": "𝑧"
}

BOLD_MAP = {
    "A": "𝐀", "B": "𝐁", "C": "𝐂", "D": "𝐃", "E": "𝐄", "F": "𝐅", "G": "𝐆", "H": "𝐇",
    "I": "𝐈", "J": "𝐉", "K": "𝐊", "L": "𝐋", "M": "𝐌", "N": "𝐍", "O": "𝐎", "P": "𝐏",
    "Q": "𝐐", "R": "𝐑", "S": "𝐒", "T": "𝐓", "U": "𝐔", "V": "𝐕", "W": "𝐖", "X": "𝐗",
    "Y": "𝐘", "Z": "𝐙",
    "a": "𝐚", "b": "𝐛", "c": "𝐜", "d": "𝐝", "e": "𝐞", "f": "𝐟", "g": "𝐠", "h": "𝐡",
    "i": "𝐢", "j": "𝐣", "k": "𝐤", "l": "𝐥", "m": "𝐦", "n": "𝐧", "o": "𝐨", "p": "𝐩",
    "q": "𝐪", "r": "𝐫", "s": "𝐬", "t": "𝐭", "u": "𝐮", "v": "𝐯", "w": "𝐰", "x": "𝐱",
    "y": "𝐲", "z": "𝐳",
    "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒", "5": "𝟓", "6": "𝟔", "7": "𝟕",
    "8": "𝟖", "9": "𝟗"
}

BOLD_ITALIC_MAP = {
    "A": "𝑨", "B": "𝑩", "C": "𝑪", "D": "𝑫", "E": "𝑬", "F": "𝑭", "G": "𝑮", "H": "𝑯",
    "I": "𝑰", "J": "𝑱", "K": "𝑲", "L": "𝑳", "M": "𝑴", "N": "𝑵", "O": "𝑶", "P": "𝑷",
    "Q": "𝑸", "R": "𝑹", "S": "𝑺", "T": "𝑻", "U": "𝑼", "V": "𝑽", "W": "𝑾", "X": "𝑿",
    "Y": "𝒀", "Z": "𝒁",
    "a": "𝒂", "b": "𝒃", "c": "𝒄", "d": "𝒅", "e": "𝒆", "f": "𝒇", "g": "𝒈", "h": "𝒉",
    "i": "𝒊", "j": "𝒋", "k": "𝒌", "l": "𝒍", "m": "𝒎", "n": "𝒏", "o": "𝒐", "p": "𝒑",
    "q": "𝒒", "r": "𝒓", "s": "𝒔", "t": "𝒕", "u": "𝒖", "v": "𝒗", "w": "𝒘", "x": "𝒙",
    "y": "𝒚", "z": "𝒛"
}

UNDERLINE_MAP = {
    "A": "𝐀̲", "B": "𝐁̲", "C": "𝐂̲", "D": "𝐃̲", "E": "𝐄̲", "F": "𝐅̲", "G": "𝐆̲", "H": "𝐇̲",
    "I": "𝐈̲", "J": "𝐉̲", "K": "𝐊̲", "L": "𝐋̲", "M": "𝐌̲", "N": "𝐍̲", "O": "𝐎̲", "P": "𝐏̲",
    "Q": "𝐐̲", "R": "𝐑̲", "S": "𝐒̲", "T": "𝐓̲", "U": "𝐔̲", "V": "𝐕̲", "W": "𝐖̲", "X": "𝐗̲",
    "Y": "𝐘̲", "Z": "𝐙̲",
    "a": "𝐚̲", "b": "𝐛̲", "c": "𝐜̲", "d": "𝐝̲", "e": "𝐞̲", "f": "𝐟̲", "g": "𝐠̲", "h": "𝐡̲",
    "i": "𝐢̲", "j": "𝐣̲", "k": "𝐤̲", "l": "𝐥̲", "m": "𝐦̲", "n": "𝐧̲", "o": "𝐨̲", "p": "𝐩̲",
    "q": "𝐪̲", "r": "𝐫̲", "s": "𝐬̲", "t": "𝐭̲", "u": "𝐮̲", "v": "𝐯̲", "w": "𝐰̲", "x": "𝐱̲",
    "y": "𝐲̲", "z": "𝐳̲",
    "0": "0̲", "1": "1̲", "2": "2̲", "3": "3̲", "4": "4̲", "5": "5̲", "6": "6̲", "7": "7̲",
    "8": "8̲", "9": "9̲", "+": "+̲", "-": "-̲", "=": "=̲", "(": "(̲", ")": ")̲", "!": "!̲",
    "?": "?̲", "#": "#̲", "@": "@̲", "&": "&̲", ".": ".̲", ",": ",̲", ":": ":̲", ";": ";̲",
    "/": "/̲"
}

STRIKETHROUGH_MAP = {
    "A": "𝐀̶", "B": "𝐁̶", "C": "𝐂̶", "D": "𝐃̶", "E": "𝐄̶", "F": "𝐅̶", "G": "𝐆̶", "H": "𝐇̶",
    "I": "𝐈̶", "J": "𝐉̶", "K": "𝐊̶", "L": "𝐋̶", "M": "𝐌̶", "N": "𝐍̶", "O": "𝐎̶", "P": "𝐏̶",
    "Q": "𝐐̶", "R": "𝐑̶", "S": "𝐒̶", "T": "𝐓̶", "U": "𝐔̶", "V": "𝐕̶", "W": "𝐖̶", "X": "𝐗̶",
    "Y": "𝐘̶", "Z": "𝐙̶",
    "a": "𝐚̶", "b": "𝐛̶", "c": "𝐜̶", "d": "𝐝̶", "e": "𝐞̶", "f": "𝐟̶", "g": "𝐠̶", "h": "𝐡̶",
    "i": "𝐢̶", "j": "𝐣̶", "k": "𝐤̶", "l": "𝐥̶", "m": "𝐦̶", "n": "𝐧̶", "o": "𝐨̶", "p": "𝐩̶",
    "q": "𝐪̶", "r": "𝐫̶", "s": "𝐬̶", "t": "𝐭̶", "u": "𝐮̶", "v": "𝐯̶", "w": "𝐰̶", "x": "𝐱̶",
    "y": "𝐲̶", "z": "𝐳̶",
    "0": "0̶", "1": "1̶", "2": "2̶", "3": "3̶", "4": "4̶", "5": "5̶", "6": "6̶", "7": "7̶",
    "8": "8̶", "9": "9̶", "+": "+̶", "-": "-̶", "=": "=̶", "(": "(̶", ")": ")̶", "!": "!̶",
    "?": "?̶", "#": "#̶", "@": "@̶", "&": "&̶", ".": ".̶", ",": ",̶", ":": ":̶", ";": ";̶",
    "/": "/̶"
}

SANS_MAP = {
    "A": "𝖠", "B": "𝖡", "C": "𝖢", "D": "𝖣", "E": "𝖤", "F": "𝖥", "G": "𝖦", "H": "𝖧",
    "I": "𝖨", "J": "𝖩", "K": "𝖪", "L": "𝖫", "M": "𝖬", "N": "𝖭", "O": "𝖮", "P": "𝖯",
    "Q": "𝖰", "R": "𝖱", "S": "𝖲", "T": "𝖳", "U": "𝖴", "V": "𝖵", "W": "𝖶", "X": "𝖷",
    "Y": "𝖸", "Z": "𝖹",
    "a": "𝖺", "b": "𝖻", "c": "𝖼", "d": "𝖽", "e": "𝖾", "f": "𝖿", "g": "𝗀", "h": "𝗁",
    "i": "𝗂", "j": "𝗃", "k": "𝗄", "l": "𝗅", "m": "𝗆", "n": "𝗇", "o": "𝗈", "p": "𝗉",
    "q": "𝗊", "r": "𝗋", "s": "𝗌", "t": "𝗍", "u": "𝗎", "v": "𝗏", "w": "𝗐", "x": "𝗑",
    "y": "𝗒", "z": "𝗓",
    "0": "𝟢", "1": "𝟣", "2": "𝟤", "3": "𝟥", "4": "𝟦", "5": "𝟧", "6": "𝟨", "7": "𝟩",
    "8": "𝟪", "9": "𝟫"
}

SANS_ITALIC_MAP = {
    "A": "𝘈", "B": "𝘉", "C": "𝘊", "D": "𝘋", "E": "𝘌", "F": "𝘍", "G": "𝘎", "H": "𝘏",
    "I": "𝘐", "J": "𝘑", "K": "𝘒", "L": "𝘓", "M": "𝘔", "N": "𝘕", "O": "𝘖", "P": "𝘗",
    "Q": "𝘘", "R": "𝘙", "S": "𝘚", "T": "𝘛", "U": "𝘜", "V": "𝘝", "W": "𝘞", "X": "𝘟",
    "Y": "𝘠", "Z": "𝘡",
    "a": "𝘢", "b": "𝘣", "c": "𝘤", "d": "𝘥", "e": "𝘦", "f": "𝘧", "g": "𝘨", "h": "𝘩",
    "i": "𝘪", "j": "𝘫", "k": "𝘬", "l": "𝘭", "m": "𝘮", "n": "𝘯", "o": "𝘰", "p": "𝘱",
    "q": "𝘲", "r": "𝘳", "s": "𝘴", "t": "𝘵", "u": "𝘶", "v": "𝘷", "w": "𝘸", "x": "𝘹",
    "y": "𝘺", "z": "𝘻"
}

SANS_BOLD_MAP = {
    "A": "𝗔", "B": "𝗕", "C": "𝗖", "D": "𝗗", "E": "𝗘", "F": "𝗙", "G": "𝗚", "H": "𝗛",
    "I": "𝗜", "J": "𝗝", "K": "𝗞", "L": "𝗟", "M": "𝗠", "N": "𝗡", "O": "𝗢", "P": "𝗣",
    "Q": "𝗤", "R": "𝗥", "S": "𝗦", "T": "𝗧", "U": "𝗨", "V": "𝗩", "W": "𝗪", "X": "𝗫",
    "Y": "𝗬", "Z": "𝗭",
    "a": "𝗮", "b": "𝗯", "c": "𝗰", "d": "𝗱", "e": "𝗲", "f": "𝗳", "g": "𝗴", "h": "𝗵",
    "i": "𝗶", "j": "𝗷", "k": "𝗸", "l": "𝗹", "m": "𝗺", "n": "𝗻", "o": "𝗼", "p": "𝗽",
    "q": "𝗾", "r": "𝗿", "s": "𝘀", "t": "𝘁", "u": "𝘂", "v": "𝘃", "w": "𝘄", "x": "𝘅",
    "y": "𝘆", "z": "𝘇",
    "0": "𝟬", "1": "𝟭", "2": "𝟮", "3": "𝟯", "4": "𝟰", "5": "𝟱", "6": "𝟲", "7": "𝟳",
    "8": "𝟴", "9": "𝟵"
}

SANS_BOLD_ITALIC_MAP = {
    "A": "𝘼", "B": "𝘽", "C": "𝘾", "D": "𝘿", "E": "𝙀", "F": "𝙁", "G": "𝙂", "H": "𝙃",
    "I": "𝙄", "J": "𝙅", "K": "𝙆", "L": "𝙇", "M": "𝙈", "N": "𝙉", "O": "𝙊", "P": "𝙋",
    "Q": "𝙌", "R": "𝙍", "S": "𝙎", "T": "𝙏", "U": "𝙐", "V": "𝙑", "W": "𝙒", "X": "𝙓",
    "Y": "𝙔", "Z": "𝙕",
    "a": "𝙖", "b": "𝙗", "c": "𝙘", "d": "𝙙", "e": "𝙚", "f": "𝙛", "g": "𝙜", "h": "𝙝",
    "i": "𝙞", "j": "𝙟", "k": "𝙠", "l": "𝙡", "m": "𝙢", "n": "𝙣", "o": "𝙤", "p": "𝙥",
    "q": "𝙦", "r": "𝙧", "s": "𝙨", "t": "𝙩", "u": "𝙪", "v": "𝙫", "w": "𝙬", "x": "𝙭",
    "y": "𝙮", "z": "𝙯"
}

CIRCLE_MAP = {
    "A": "Ⓐ", "B": "Ⓑ", "C": "Ⓒ", "D": "Ⓓ", "E": "Ⓔ", "F": "Ⓕ", "G": "Ⓖ", "H": "Ⓗ",
    "I": "Ⓘ", "J": "Ⓙ", "K": "Ⓚ", "L": "Ⓛ", "M": "Ⓜ", "N": "Ⓝ", "O": "Ⓞ", "P": "Ⓟ",
    "Q": "Ⓠ", "R": "Ⓡ", "S": "Ⓢ", "T": "Ⓣ", "U": "Ⓤ", "V": "Ⓥ", "W": "Ⓦ", "X": "Ⓧ",
    "Y": "Ⓨ", "Z": "Ⓩ",
    "a": "ⓐ", "b": "ⓑ", "c": "ⓒ", "d": "ⓓ", "e": "ⓔ", "f": "ⓕ", "g": "ⓖ", "h": "ⓗ",
    "i": "ⓘ", "j": "ⓙ", "k": "ⓚ", "l": "ⓛ", "m": "ⓜ", "n": "ⓝ", "o": "ⓞ", "p": "ⓟ",
    "q": "ⓠ", "r": "ⓡ", "s": "ⓢ", "t": "ⓣ", "u": "ⓤ", "v": "ⓥ", "w": "ⓦ", "x": "ⓧ",
    "y": "ⓨ", "z": "ⓩ",
    "0": "⓪", "1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦",
    "8": "⑧", "9": "⑨"
}

MONO_MAP = {
    "A": "𝙰", "B": "𝙱", "C": "𝙲", "D": "𝙳", "E": "𝙴", "F": "𝙵", "G": "𝙶", "H": "𝙷",
    "I": "𝙸", "J": "𝙹", "K": "𝙺", "L": "𝙻", "M": "𝙼", "N": "𝙽", "O": "𝙾", "P": "𝙿",
    "Q": "𝚀", "R": "𝚁", "S": "𝚂", "T": "𝚃", "U": "𝚄", "V": "𝚅", "W": "𝚆", "X": "𝚇",
    "Y": "𝚈", "Z": "𝚉",
    "a": "𝚊", "b": "𝚋", "c": "𝚌", "d": "𝚍", "e": "𝚎", "f": "𝚏", "g": "𝚐", "h": "𝚑",
    "i": "𝚒", "j": "𝚓", "k": "𝚔", "l": "𝚕", "m": "𝚖", "n": "𝚗", "o": "𝚘", "p": "𝚙",
    "q": "𝚚", "r": "𝚛", "s": "𝚜", "t": "𝚝", "u": "𝚞", "v": "𝚟", "w": "𝚠", "x": "𝚡",
    "y": "𝚢", "z": "𝚣",
    "0": "𝟶", "1": "𝟷", "2": "𝟸", "3": "𝟹", "4": "𝟺", "5": "𝟻", "6": "𝟼", "7": "𝟽",
    "8": "𝟾", "9": "𝟿"
}

SUP_MAP = {
    "A": "ᴬ", "B": "ᴮ", "C": "ꟲ", "D": "ᴰ", "E": "ᴱ", "F": "ꟳ", "G": "ᴳ", "H": "ᴴ",
    "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ", "N": "ᴺ", "O": "ᴼ", "P": "ᴾ",
    "Q": "ꟴ", "R": "ᴿ", "S": "ˢ", "T": "ᵀ", "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ",
    "Y": "ʸ", "Z": "ᶻ",
    "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ",
    "i": "ⁱ", "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ",
    "q": "𐞥", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ",
    "y": "ʸ", "z": "ᶻ",
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷",
    "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"
}

SUB_MAP = {
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ", "l": "ₗ", "m": "ₘ",
    "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ",
    "x": "ₓ",
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇",
    "8": "₈", "9": "₉", "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎"
}

SMALL_CAPS_MAP = {
    "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ꜰ", "G": "ɢ", "H": "ʜ",
    "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ", "M": "ᴍ", "N": "ɴ", "O": "ᴏ", "P": "ᴘ",
    "Q": "ꞯ", "R": "ʀ", "S": "ꜱ", "T": "ᴛ", "U": "ᴜ", "V": "ᴠ", "W": "ᴡ", "X": "x",
    "Y": "ʏ", "Z": "ᴢ",
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ", "h": "ʜ",
    "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ",
    "q": "ꞯ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
    "y": "ʏ", "z": "ᴢ"
}
# fmt: on

_DICTS: list[dict[str, str]] = [
    v for k, v in globals().items() if k.endswith("_MAP") and k != "NORMAL_MAP"
]
NORMAL_MAP = {v: k for d in _DICTS for k, v in d.items()}

def _to_map(mapping: dict[str, str], text: str) -> str:
    """Convert text to a specific format using the provided mapping."""
    parts = (mapping.get(c, c) for c in regex.findall(r"\X", text))
    parts = (x for x in parts if x)
    return "".join(parts)


def to_normal(text: str) -> str:
    """Convert text from various formats back to normal ASCII characters.

    :param text: the input text to convert
    :return: the converted text with all characters mapped back to their normal form
    """
    return _to_map(NORMAL_MAP, text)


def _normalize_then_to_map(mapping: dict[str, str], text: str) -> str:
    """Convert text to a specific format using the provided mapping. Normalize first.

    :param mapping: a dictionary mapping characters to their formatted counterparts
    :param text: the input text to convert
    :return: the converted text
    """
    text = to_normal(text)
    return _to_map(mapping, text)


to_italic = ft.partial(_normalize_then_to_map, ITALIC_MAP)
to_bold = ft.partial(_normalize_then_to_map, BOLD_MAP)
to_bold_italic = ft.partial(_normalize_then_to_map, BOLD_ITALIC_MAP)
to_underline = ft.partial(_normalize_then_to_map, UNDERLINE_MAP)
to_strikethrough = ft.partial(_normalize_then_to_map, STRIKETHROUGH_MAP)
to_sans = ft.partial(_normalize_then_to_map, SANS_MAP)
to_sans_italic = ft.partial(_normalize_then_to_map, SANS_ITALIC_MAP)
to_sans_bold = ft.partial(_normalize_then_to_map, SANS_BOLD_MAP)
to_sans_bold_italic = ft.partial(_normalize_then_to_map, SANS_BOLD_ITALIC_MAP)
to_circle = ft.partial(_normalize_then_to_map, CIRCLE_MAP)
to_mono = ft.partial(_normalize_then_to_map, MONO_MAP)
to_sup = ft.partial(_normalize_then_to_map, SUP_MAP)
to_sub = ft.partial(_normalize_then_to_map, SUB_MAP)
to_small_caps = ft.partial(_normalize_then_to_map, SMALL_CAPS_MAP)
