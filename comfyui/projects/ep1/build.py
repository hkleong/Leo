#!/usr/bin/env python3
"""第一集全集：从紧凑镜头表生成 H3 Ref2VA 六段式提示词 + jobs.json"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.abspath(os.path.join(HERE, '../../out')); SH = O + '/sheets'; P8 = os.path.abspath(os.path.join(HERE, '../../../p8'))

UNI_M = "the Tianheng Academy uniform: a navy blazer with a crossed hanfu-style collar edged in thin pale-grey piping and a small white sword-and-cloud emblem, a white mandarin-collar shirt and charcoal-grey trousers"
UNI_F = "the Tianheng Academy uniform: a fitted navy blazer with a crossed hanfu-style collar edged in thin pale-grey piping and a small white sword-and-cloud emblem, a white mandarin-collar blouse, a knee-length charcoal-grey pleated skirt and dark navy knee socks"
C = {  # key: (definition, pics, voice)
 'LX': ("the young man in {p}: Lin Xiao, a handsome, quiet East Asian student with slightly long tousled black hair with a faint dark navy sheen, calm deep-set eyes and a defined jawline, wearing " + UNI_M + ", an old bronze coin on a red cord, and a cloth-wrapped sword slung on his back",
        [f'{SH}/linxiao/linxiao_half.png', f'{SH}/linxiao/linxiao_face.png'], "the young man with a low, calm, relaxed voice"),
 'SQS': ("the young woman in {p}: Shen Qingshuang, the student council president, a cool, beautiful East Asian girl with a long black high ponytail tied with a white silk ribbon, wearing " + UNI_F + ", with a slender silver jian sword with a jade tassel at her hip",
        [f'{SH}/shenqingshuang/shenqingshuang_half.png', f'{SH}/shenqingshuang/shenqingshuang_face.png'], "the young woman with a cool, clear, steady voice"),
 'SDZ': ("the young man in {p}: Shi Dazhuang, a huge, very muscular East Asian student with a buzz cut and a friendly broad face, wearing " + UNI_M + " stretched over his body, his forearms and fists wrapped in old cloth bandages with faint golden runes",
        [f'{SH}/shidazhuang/shidazhuang_half.png', f'{SH}/shidazhuang/shidazhuang_face.png'], "the big young man with a deep, warm, slightly loud voice"),
 'JDB': ("the young man in {p}: Jin Duobao, a rich, easygoing East Asian student with ash-brown hair, thin gold-rimmed round glasses, a green jade pendant on a cord and a gold watch, wearing " + UNI_M + ", a small bronze pill gourd at his belt",
        [f'{SH}/jinduobao/jinduobao_half.png', f'{SH}/jinduobao/jinduobao_face.png'], "the young man with a light, playful, slightly lazy voice"),
 'TXL': ("the young woman in {p}: Tang Xiaoling, a lively East Asian girl with shoulder-length dark brown hair, soft bangs and two small buns, a small bell bracelet on her wrist, wearing " + UNI_F + ", often holding a smartphone on a selfie stick",
        [f'{SH}/tangxiaoling/tangxiaoling_half.png', f'{SH}/tangxiaoling/tangxiaoling_face.png'], "the young woman with a bright, lively, sweet voice"),
 'MHY': ("the man in {p}: Mo Hanyuan, a tall pale demonic cultivator with long black hair half tied in a high knot with a black jade hairpin, cold narrow eyes, a long black high-collar coat with dark crimson cloud embroidery, black leather gloves, red beads on his wrist and a slim black jian sword",
        [f'{P8}/vface_0.png', f'{P8}/v_1.png'], "the young man with a smooth, cold, low voice"),
 'YZG': ("the man in {p}: Dean Yan Zhenggang, a stern middle-aged East Asian man with neat slicked-back dark hair, a navy suit, white shirt and dark red tie, a long black academic robe draped over his shoulders, carrying a black wooden disciplinary ruler",
        [f'{O}/t_dean_0.png'], "the middle-aged man with a stern, firm, clipped voice"),
 'YSZ': ("the old man in {p}: Principal Yun Shouzhuo, a kind elderly East Asian man with long white hair in a small topknot with a wooden pin and a long white beard, wearing a long grey knitted robe over a white Chinese-collar shirt and dark wide trousers, holding a small teacup",
        [f'{O}/t_principal_1.png'], "the old man with a slow, gentle, slightly raspy voice"),
 'HLF': ("the man in {p}: Hu Laifu, the alchemy teacher, a chubby cheerful middle-aged East Asian man with messy black hair and goggles pushed up on his forehead, wearing a scorched white lab coat over a mustard vest and checked shirt",
        [f'{O}/t_alchemy_1.png'], "the middle-aged man with a cheerful, jolly voice"),
 'GTS': ("the man in {p}: Guan Tieshan, the PE teacher, a bald, extremely muscular middle-aged East Asian man with a big grin, wearing a black tank top, a red jacket tied around his waist, black training pants, a whistle on a cord and red wristbands",
        [f'{O}/t_pe_m_0.png'], "the middle-aged man with a hearty, booming voice"),
 'WYN': ("the woman in {p}: Wen Yining, the homeroom teacher, a gentle East Asian woman in her thirties with shoulder-length wavy brown hair and thin glasses, wearing a cream cardigan over a light blue shirt and a long beige pleated skirt, a staff ID on a lanyard",
        [f'{O}/t_homeroom_1.png'], "the woman with a soft, gentle voice"),
 'JYZ': ("the young man in {p}: Jiang Yizhou, a vain handsome East Asian student with neat swept black hair and two swords crossed on his back; at school he wears the Tianheng uniform (<UNI>) (exactly as in the picture)",
        [f'{O}/cls/c01_0_uni_0.png'], "the young man with a smug, slightly nasal voice"),
 'QTS': ("the young man in {p}: Qi Tiansuan, a laid-back East Asian student with bleached blond hair under a black bucket hat, holding a smartphone; at school he wears the Tianheng uniform (<UNI>) (exactly as in the picture)",
        [f'{O}/cls/c08_0_uni_0.png'], "the young man with a lazy, mumbling voice"),
 'LXM': ("the young woman in {p}: Lu Xiaoman, a sweet, spacey East Asian girl with long light-brown hair and a pink bow, with a chubby orange tabby cat named Yuanbao sitting on her shoulder; at school she wears the Tianheng uniform (<UNI>) (she appears exactly as in the picture; she never wears the yellow cardigan or sailor collar)",
        [f'{O}/cls/c03_1_uni_0.png'], "the young woman with a soft, slow, airy voice"),
 'FDP': ("the young man in {p}: Fan Dapao, a stocky East Asian student with curly black hair and welding goggles on his head, a clunky brass mechanical arm strapped to his right arm and a tool belt; at school he wears the Tianheng uniform (<UNI>) (exactly as in the picture)",
        [f'{O}/cls/c06_0_uni_0.png'], "the young man with a nervous, quick voice"),
 'YYT': ("the young woman in {p}: Ye Yutang, a gentle East Asian girl with a long black side braid, wearing a white doctor's coat over " + UNI_F + ", holding a long silver acupuncture needle",
        [f'{O}/cls/c05_0_uni_0.png'], "the young woman with a soft, gentle, sweet voice"),
 'UNI': ("the Tianheng Academy school uniform design shown in {p} (girls' version; the boys' version is the same navy crossed-collar blazer with thin pale-grey piping and the small white emblem, over a white mandarin-collar shirt, with charcoal-grey trousers). Every student in this video, including all background extras, wears exactly this uniform: a crossed hanfu-style wrap collar, no lapels, no neckties, no bow ties", [f'{O}/uni/uniform_f.png'], ""),
 'BOSS': ("a mysterious man seated on a high throne, completely in shadow so that his face is never visible, only the outline of a black robe and one pale hand resting on the armrest", [], "the man with a deep, distant, echoing voice"),
}
L = {
 'CLIFF': "a rocky mountain cliff edge at night under a full moon, with windswept pine trees, looking down into a deep misty valley where Tianheng Academy glows with warm lights: school buildings with sweeping traditional Chinese tiled roofs, a tall pagoda and a wide stone plaza",
 'GATE': "the main gate of Tianheng Academy on a sunny morning: a grand traditional stone gateway with a dark tiled roof, a modern tree-lined campus road beyond it with a fork where the path splits left and right beside a wooden signpost, students in navy blazers walking in",
 'OFFICE': "a bright student council office in the morning, with a long dark wooden meeting table, tall windows with paper-lattice details, bookshelves, a whiteboard at the head of the table and a calligraphy scroll, sunlight streaming in",
 'PLAZA': "a huge sunlit stone training plaza of a xianxia academy, surrounded by traditional tiled-roof halls with navy banners, with a crowd of students in navy blazers watching from behind a rope line; in the center stands the Tianheng Mirror, a tall round bronze mirror taller than a man on a carved stone pedestal, its polished surface glowing with soft white light and never showing any text, numbers or reflections of faces",
 'ROOF': "the flat wet concrete rooftop of a modern high school at night, with puddles, a chain-link fence, water tanks along the edge and a glittering city skyline beyond",
 'INFIRM': "a bright, clean school infirmary in the late afternoon, with white curtained beds in a row, a wooden medicine cabinet with many small herb drawers and warm sunlight through the windows",
 'DUSK': "the same huge stone training plaza at dusk, completely empty, orange sunset light and long shadows, the tall round bronze Tianheng Mirror on its carved stone pedestal in the center, never showing any text or numbers",
 'EAVES': "a quiet covered wooden corridor with dark tiled eaves at the edge of the plaza at dusk, a small ginkgo tree dropping golden leaves",
 'HALL': "a vast, dark stone hall of the rival Xuanming Academy, black stone pillars, rows of dim crimson lanterns, a long red carpet leading to a high black throne in deep shadow",
}
STYLE = ("Acting is natural and understated: subtle, realistic facial expressions and small natural gestures, no exaggerated mugging, no cartoonish reactions, no wide-open shouting mouths. "
         "All dialogue is spoken in Mandarin Chinese with a natural, casual Taiwanese accent, like a Taiwanese idol drama. Phone screens, wristbands and signs never show readable text.")

SEG = []
def seg(id, dur, loc, look, summary, shots, sound, music="N/A"):
    SEG.append(dict(id=id, dur=dur, loc=loc, look=look, summary=summary, shots=shots, sound=sound, music=music))

UNI_SEGS = {'05a','05b','05c','05d','06a','06b','06c','06d','06e','07a','07b'}
def build(s):
    if s['id'] in UNI_SEGS and '<UNI>' not in s['summary']: s['summary'] += ' All students wear <UNI>.'
    text = s['summary'] + ' '.join(t for _, t in s['shots'])
    keys = [k for k in C if '<' + k + '>' in text]
    keys.sort(key=lambda k: text.index('<' + k + '>'))
    num = {k: i + 1 for i, k in enumerate(keys)}; locn = len(keys) + 1
    pics, defs = [], []
    for k in keys:
        d, ps, _ = C[k]
        labels = []
        for p in (ps[:1] if len(keys) > 3 else ps):
            pics.append(p); labels.append(f'<Picture {len(pics)}>')
        d = d.format(p=' and '.join(labels)) if labels else d
        defs.append(f'<Subject {num[k]}> is {d}.')
    defs = [re.sub(r'<(\w+)>', lambda m: f'<Subject {num[m.group(1)]}>' if m.group(1) in num else m.group(0), d) for d in defs]
    defs.append(f'<Subject {locn}> is the location: {L[s["loc"]]}.')
    def sub(t):
        def say(m):
            k, how, line = m.group(1), m.group(2), m.group(3)
            v = C[k][2]; v = v[0].upper() + v[1:]
            return f"{v} (S{num[k]}, in a Taiwanese accent) says{(', ' + how) if how else ''}: <d>[Chinese] {line}</d>"
        t = re.sub(r'@(\w+)(?:\{([^}]*)\})?:「([^」]*)」', say, t)
        for k in keys: t = t.replace('<' + k + '>', f'<Subject {num[k]}>')
        return t.replace('<LOC>', f'<Subject {locn}>')
    shots = []
    for i, (tm, t) in enumerate(s['shots']):
        t = sub(t)
        shots.append(f'[Shot {i+1}] {t}' if i == 0 else f'[Shot {i+1}] At {tm}, the shot cuts to {t}')
    ret = []
    for k in keys + ['LOC']:
        lab = f'<Subject {locn}>' if k == 'LOC' else f'<Subject {num[k]}>'
        ins = [f'[Shot {i+1}]' for i, sh in enumerate(shots) if lab in sh]
        if not ins: ins = ['[Shot 1]']
        what = 'the location and its lighting' if k == 'LOC' else 'the uniform design stays identical on every student' if k == 'UNI' else 'face, hair, outfit and props stay identical to the reference'
        ret.append(f'{lab} (appears in {", ".join(ins)}): fully_preserved - {what}.')
    out = ("subject_definitions:\n" + '\n'.join(defs) + "\n\nsummary:\n[reference generation] " + sub(s['summary']) +
           "\n\nretention_analysis:\n" + '\n'.join(ret) + "\n\ndetailed_description:\n" + s['look'] + ' ' + STYLE + '\n' + '\n'.join(shots) +
           "\n\noverall_soundscape:\nNo background music; only diegetic sound and dialogue. " + s['sound'] + "\n\nnon_diegetic_music:\n" + s['music'] + "\n")
    return out, pics

DAY = "The target video uses a bright, warm, photorealistic live-action Taiwanese school drama style with natural daylight, natural colors and clean, unhurried cuts."
NIGHT = "The target video uses a photorealistic live-action xianxia drama style at night, cold blue light, deep shadows and saturated crimson energy glows, with tense, controlled pacing."

# ---------------- 第 1 场 冷开场 ----------------
seg('01a', 12.5, 'CLIFF', NIGHT, "<MHY> stands alone on <LOC> at night, watches a bronze compass needle lock onto the academy below, says one quiet line, and ignites crimson fire in his palm as his eyes begin to glow crimson.", [
 ('', "An extreme wide shot from behind and slightly above <MHY>, who stands with his back to the camera at the very edge of the cliff on the right third of the frame, his long black coat and hair moving in the wind; far below, the misty valley and the glowing academy. The camera drifts slowly forward over his shoulder. Howling wind."),
 ('00:03.000', "an insert close-up, outdoors on the dark moonlit cliff with blurred mist and pines behind, of his black-gloved left hand holding an old round bronze compass engraved with trigrams; the thin needle spins, slows, then locks pointing straight ahead toward the valley, trembling slightly. Dry ticking that stops with a click."),
 ('00:05.500', "a close-up of <MHY>'s face, side-lit by cold moonlight, his eyes dark and not glowing, looking down toward the academy with a calm, cold gaze; the faintest smile. @MHY{quietly, almost to himself}:「一年前消失的那道剑气……原来躲在这里啊。」"),
 ('00:09.300', "a medium shot from the side: <MHY> slowly turns his right hand palm up in front of his chest and a small dark crimson flame ignites in his gloved palm, lighting his face from below."),
 ('00:11.000', "an extreme close-up of his eyes as they slowly begin to glow crimson, the flame flickering in them. A low crackle and a deep hum swelling."),
], "Strong mountain wind, rustling pines, distant night insects, the ticking compass, a low crackling flame.")

# ---------------- 第 2 场 上学路 ----------------
seg('02a', 11, 'GATE', DAY, "<SDZ> rides an electric scooter with a delivery box through <LOC>, checks the glowing wristband on his arm and says a line to himself.", [
 ('', "A wide shot of <LOC>: <SDZ>, in his navy school blazer, rides a small electric scooter with a square delivery box on the back through the stone gateway, weaving gently around walking students, and brakes to a stop near the camera."),
 ('00:03.500', "a close-up of his bandaged left forearm as he raises it: a thin metal spirit-test wristband on it glows with a soft blue light, showing no readable text."),
 ('00:05.000', "a medium close-up of <SDZ> on the scooter, looking at the wristband, then exhaling and nodding to himself with quiet determination. @SDZ{under his breath}:「还差五十……今天一定要破四千。」"),
 ('00:08.800', "a medium shot as he lifts a takeout bag from the delivery box, then grins and waves it at someone off-screen. @SDZ:「欸，你的早餐啦！」"),
], "Morning birds, students chatting, the soft whir and brake squeak of the scooter, a plastic bag rustling.")

seg('02b', 11, 'GATE', DAY, "<JDB> steps out of a sleek sports car at <LOC>, swallows pills from his gourd, watches his wristband flicker and reacts dryly.", [
 ('', "A medium-wide shot: a sleek silver sports car pulls up at the curb by <LOC>; the door swings up and <JDB>, in his navy blazer and gold round glasses, steps out unhurriedly, adjusting his glasses."),
 ('00:03.000', "a close-up as he tips three small golden pills from his bronze gourd into his palm and tosses them into his mouth, chewing calmly."),
 ('00:05.000', "an insert close-up of the spirit-test wristband on his wrist: its blue glow flares brighter, then flickers weakly, then flares again, unstable. No readable text."),
 ('00:07.000', "a medium close-up of <JDB> frowning slightly at the wristband, tapping it twice with a finger. @JDB{flatly, a little puzzled}:「……蛤？这批是不是过期了啊？」 He shrugs and walks toward the gate."),
], "A sports car engine idling, the door hissing, pills rattling in a gourd, a faint electronic flicker sound, morning crowd chatter.")

seg('02c', 11, 'GATE', DAY, "<TXL> walks through <LOC> livestreaming on her phone on a selfie stick, talking warmly to her viewers.", [
 ('', "A medium tracking shot walking backward in front of <TXL> as she walks along the tree-lined campus road toward the camera, holding up her phone on a selfie stick, smiling naturally at the screen."),
 ('00:02.000', "a close-up of <TXL> from the phone's point of view, her face filling the frame, small floating heart icons drifting up the edge of the frame. @TXL{cheerfully, chatting}:「哈啰大家早～今天是我们学校的灵测日喔！」"),
 ('00:06.000', "a medium shot as she glances at the screen, giggles softly at a comment, and gives a small wave. @TXL:「礼物多一点，我等一下就冲给你们看～」 The bell on her wrist jingles."),
], "Morning birds, footsteps on pavement, a soft notification chime, the small jingle of a bell, crowd chatter.")

seg('02d', 13, 'GATE', DAY, "<SQS> stops at the fork in the road at <LOC>, studies a campus map, and confidently walks the wrong way; <LX> walks past without a word and turns the right way, and she follows him without noticing her mistake.", [
 ('', "A wide shot of the fork in the campus road beside the wooden signpost: <SQS>, in her navy blazer and high ponytail, stands in the middle holding a folded paper campus map, looking from the map to the left path and back."),
 ('00:02.500', "a medium close-up of <SQS>, brow slightly furrowed, then she nods decisively. @SQS{quietly, to herself}:「应该是……这边吧。」 She turns toward the left path."),
 ('00:05.500', "a medium shot from behind <SQS> as she takes a few steps down the left path; behind her, in the background, <LX> walks along with his hands in his pockets, his cloth-wrapped sword on his back, and calmly turns down the right path without stopping."),
 ('00:08.500', "a medium close-up of <SQS> as she notices <LX> heading the other way, pauses, glances at her map, then quietly turns around and follows a few steps behind him, as if nothing happened."),
 ('00:11.000', "a close-up of <LX> walking, eyes forward; the corner of his mouth lifts very slightly."),
], "Morning birds, leaves rustling, paper map rustling, footsteps on pavement.")

# ---------------- 第 3 场 学生会办公室 ----------------
seg('03a', 14.5, 'OFFICE', DAY, "A light morning meeting in <LOC>: <TXL> reads a campus forum post about <LX>'s spiritual power, <JDB> asks about it and laughs quietly, while <LX> calmly drinks tea and <SDZ> and <SQS> look on.", [
 ('', "A wide shot of <LOC>: <SQS> stands at the head of the long table on the far side in front of the whiteboard, looking through a folder. On the left side of the table sit <TXL> and, beside her, <JDB>; on the right side sit <SDZ> and, nearest the camera, <LX>, who holds a small white teacup."),
 ('00:02.500', "a medium close-up of <TXL> on the left side of the table, scrolling her phone, then looking up with a mischievous little smile. @TXL:「欸，你们看，论坛又在讨论林逍了。」"),
 ('00:05.500', "a medium shot of <JDB> beside her, leaning over to look, pushing up his glasses. @JDB:「讨论什么？」"),
 ('00:07.000', "a close-up of <TXL> reading from the screen, trying not to smile. @TXL:「‘转学一年从来没灵测过，他到底几点？’最高赞说……八十七，不能再多了。」"),
 ('00:12.000', "a medium shot of <JDB> covering his mouth, his shoulders shaking with a quiet laugh. @JDB{softly}:「噗……八十七喔。」"),
], "Quiet office ambience, birds outside, a teacup clinking softly, light laughter.")

seg('03b', 14, 'OFFICE', DAY + " Throughout this video Shen Qingshuang's sword stays sheathed at her hip.", "Continuing in <LOC>: <SDZ> tries to defend <LX>, <LX> answers mildly, and <SQS> closes her folder and gets the meeting back on track.", [
 ('', "A medium two-shot on the right side of the table, <LX> nearest the camera and <SDZ> beside him: <SDZ> puts a big bandaged hand on <LX>'s shoulder and gives the others a slightly awkward, sincere look. @SDZ:「欸，不要这样啦，人家八十七也是……也是有在努力啊。」"),
 ('00:04.500', "a close-up of <LX>, unbothered, taking a slow sip of tea and setting the cup down. @LX{mildly}:「还好啦，我觉得八十七蛮好的。」"),
 ('00:08.000', "a medium-wide shot from the foot of the table looking toward <SQS> standing at the head of the table in front of the whiteboard: <TXL> and <JDB> sit on the LEFT side of the frame and <SDZ> and <LX> sit on the RIGHT side of the frame, exactly as seated before; <SQS> closes her folder with a firm snap; everyone goes quiet. @SQS{calm but firm}:「好了喔。今天学生会要负责维持秩序，不是在这边聊八卦。」"),
 ('00:12.500', "a medium shot of the left side of the same table in the same office: <TXL> quickly puts her phone face down, <JDB> beside her straightens his glasses and sits up."),
], "Quiet office ambience, a folder snapping shut, a phone set down on wood, then silence.")

seg('03c', 12, 'OFFICE', DAY + " Throughout this video Shen Qingshuang's sword stays sheathed at her hip.", "<SQS> walks over to the seated <LX> and quietly tells him to stay behind her during the test; he agrees, and after she leaves <TXL> and <JDB> exchange a look.", [
 ('', "A medium shot in the same office: <SQS>, her sword sheathed in its scabbard at her hip and her hands empty, walks along the right side of the table and stops beside the seated <LX>, bending slightly toward him; she is on the left of the frame and he is on the right, looking up at her."),
 ('00:02.000', "a close-up of <SQS>, her expression softening a little, speaking quietly. @SQS{quietly}:「等一下测试，你就站我后面，知道吗？」"),
 ('00:05.500', "a close-up of <LX> looking up at her for a beat. @LX{softly}:「……喔，好。」"),
 ('00:07.500', "a medium shot as <SQS> straightens up and walks toward the office door, her sword still sheathed at her hip; <LX> watches her go, the faintest smile."),
 ('00:10.000', "a two-shot on the left side of the same long wooden table: <TXL> and <JDB> slowly turn and exchange a meaningful look, eyebrows slightly raised."),
], "Quiet office ambience, footsteps on a wooden floor, a door closing softly.")

# ---------------- 第 4 场 灵测开幕 ----------------
seg('04a', 13, 'PLAZA', DAY, "The opening of Spirit Test Day at <LOC>: <YZG> addresses the whole school beside the giant mirror while <WYN> stands nearby.", [
 ('', "An extreme wide high-angle shot of <LOC>: hundreds of students in navy blazers stand in neat rows facing the giant bronze mirror; banners move in the breeze."),
 ('00:02.500', "a medium shot of <YZG> standing beside the mirror, holding the black wooden ruler behind his back, scanning the crowd with a stern face. <WYN> stands a step behind him holding a clipboard. @YZG:「灵测结果会决定这学期的修炼资源分配。」"),
 ('00:07.000', "a close-up of <YZG> tapping the ruler once in his palm. @YZG:「每个人照顺序上来，不准插队，不准作弊，听到没有？」"),
 ('00:11.000', "a wide shot of the rows of students answering in unison, a little half-hearted. Students: <d>[Chinese] 听到了——</d>"),
], "Large outdoor crowd murmuring, banners flapping, a ruler tapping a palm, a crowd answering in unison.")

seg('04b', 14, 'PLAZA', DAY, "<YSZ> sits drinking tea at the edge of <LOC> as a falling leaf freezes in midair beside him; when the mirror's scanning light passes over him it glitches and goes dark, and <YZG> has to restart it.", [
 ('', "A medium shot of <YSZ> sitting on a wooden chair under a ginkgo tree at the edge of the plaza, sipping tea calmly; a golden ginkgo leaf drifts down beside him and stops completely still in midair, hanging there."),
 ('00:03.500', "a wide shot: a soft beam of white light sweeps out from the giant mirror across the front rows; as it passes over <YSZ>, the mirror crackles, flickers wildly and goes completely dark with an electric buzz. The crowd falls silent."),
 ('00:07.000', "a close-up of <YSZ> taking another unhurried sip, then speaking mildly. @YSZ:「老毛病了，拍一拍就好。」"),
 ('00:10.000', "a medium shot of <YZG>, slightly embarrassed, walking to the mirror and giving its bronze frame two firm slaps with his palm; the mirror lights back up with a soft hum. A few students stifle laughs."),
], "Wind in the ginkgo tree, a crackling electric buzz then silence, two hollow metal slaps, a soft hum, muffled giggles.")

# ---------------- 第 5 场 同学篇 ----------------
seg('05a', 11, 'PLAZA', DAY, "While waiting in line at <LOC>, <QTS> casts a fortune on his phone app and announces a bad omen; <JYZ> brushes it off.", [
 ('', "A medium shot in the waiting line: <QTS>, under his bucket hat, frowns at the glowing trigram pattern on his phone screen."),
 ('00:02.500', "a close-up of <QTS> looking up, completely serious. @QTS{flatly}:「我刚刚帮学校算了一卦……今天，大凶。」"),
 ('00:06.000', "a medium shot of <JYZ> beside him, not even looking over, adjusting the swords on his back. @JYZ:「你算的喔？那就是大吉啦。」 Students around them chuckle quietly."),
 ('00:09.500', "a close-up of <QTS> looking back down at his phone, unconvinced, tilting his head."),
], "Crowd murmuring, a soft app chime, quiet chuckles.")

seg('05b', 12, 'PLAZA', DAY, "<LXM> places her hand on the mirror at <LOC> and gets a faint glow; her cat Yuanbao lazily touches the mirror with a paw and it blazes far brighter, leaving the crowd silent.", [
 ('', "A medium shot: <LXM>, with the chubby orange cat on her shoulder, presses her small hand on the giant mirror; a faint, small glow rises in the mirror and stays low."),
 ('00:03.500', "a close-up of the orange cat on her shoulder yawning, then lazily stretching out one paw and tapping the mirror surface."),
 ('00:05.500', "a wide shot: the whole mirror suddenly blazes with bright golden light from bottom to top; the crowd behind the rope goes completely silent, a few students' mouths slightly open."),
 ('00:08.500', "a close-up of <LXM> turning her head to the cat, speaking gently. @LXM:「元宝……你不要乱碰啦。」 The cat blinks slowly."),
], "Crowd murmuring that stops abruptly, a soft hum rising into a bright resonant tone, a cat's small yawn, silence.")

seg('05c', 12, 'PLAZA', DAY, "<FDP>'s mechanical arm malfunctions as he steps up to the mirror at <LOC> and <GTS> catches it with one hand.", [
 ('', "A medium shot: <FDP> steps up to the mirror and raises his brass mechanical arm; it suddenly whirs, sparks and jerks out of control, swinging toward the mirror."),
 ('00:02.500', "a close-up of a big hand catching the brass arm by the wrist one inch from the mirror: <GTS> holds it still with one hand, totally relaxed."),
 ('00:04.500', "a medium two-shot: <GTS> smiles at <FDP>. @GTS:「小范，下次上来之前，手臂先关机好不好？」"),
 ('00:08.500', "a close-up of <FDP>, embarrassed, fumbling to switch off the arm. @FDP:「对不起老师……我马上关。」 The arm powers down with a sad whine."),
], "Crowd murmuring, mechanical whirring and sparking, a heavy metal clank when caught, a power-down whine.")

seg('05d', 11, 'PLAZA', DAY, "<JYZ> finishes his test at <LOC>, then turns to the student council members and makes a smug remark; <SQS> ignores him.", [
 ('', "A medium shot: <JYZ> takes his hand off the mirror as a respectable silver glow fades; he brushes his hair back with satisfaction."),
 ('00:03.000', "a medium shot as he strolls past the student council standing by the rope, <SQS> at the front with <LX> behind her, and stops, glancing at them sideways. @JYZ:「学生会也不过就这样嘛。」"),
 ('00:06.500', "a close-up of <JYZ> smirking slightly. @JYZ:「明年，会长就是我的了。」"),
 ('00:09.000', "a close-up of <SQS>, not even looking at him, eyes on the mirror, completely calm."),
], "Crowd murmuring, a fading hum, footsteps on stone.")

# ---------------- 第 6 场 学生会篇 ----------------
seg('06a', 11, 'PLAZA', DAY, "<TXL> tests at the mirror at <LOC> while livestreaming; viewers send gifts and her glow rises a little, and she is quietly thrilled.", [
 ('', "A medium shot: <TXL> stands before the mirror, her phone propped up on the selfie stick beside her, one palm on the mirror, a modest glow inside it."),
 ('00:02.500', "a close-up of <TXL> glancing at the phone. @TXL{softly, to her viewers}:「家人们，帮我一下下～」"),
 ('00:05.000', "an insert of the phone screen filled with floating hearts and small gift icons, no readable text, chiming rapidly."),
 ('00:06.500', "a medium shot: the mirror's glow climbs a little higher; <TXL> presses her lips together, eyes lighting up. @TXL{quietly}:「有涨欸……谢谢你们！」"),
], "Crowd murmuring, rapid soft gift chimes, a rising hum, a bell jingling.")

seg('06b', 14, 'PLAZA', DAY, "<JDB> swallows a pill before testing at <LOC>; his glow surges then backfires in a puff of black smoke, and <HLF> praises it in his own way.", [
 ('', "A medium shot: <JDB> pops a golden pill into his mouth and places his palm on the mirror; the light inside surges up fast."),
 ('00:03.000', "a close-up: a small puff of black smoke bursts out from his collar with a muffled pop; his glasses are smudged with soot; the mirror's light drops back down."),
 ('00:05.000', "a medium shot of <JDB> coughing lightly and waving the smoke away with a resigned look."),
 ('00:07.000', "a medium shot of <HLF> by the rope, clapping, beaming proudly. @HLF:「不错喔！这个炸法，有我当年的味道。」"),
 ('00:10.500', "a close-up of <JDB> wiping his glasses, deadpan. @JDB:「老师……这应该不是在称赞吧？」"),
], "Crowd murmuring, a rising hum, a muffled pop, light coughing, clapping, a few laughs.")

seg('06c', 13, 'PLAZA', DAY, "<SDZ> tests at the mirror at <LOC> with everything he has; the light stalls just short of the top, he sinks to his knees disappointed, and <GTS> pulls him up with encouragement.", [
 ('', "A wide shot: <SDZ>, in his navy blazer, steps up to the mirror, rolls his shoulders, and presses his right palm flat on it. The crowd quiets."),
 ('00:02.500', "a close-up of <SDZ>'s face in profile, jaw set, breathing hard through his nose, a vein rising on his temple, a thin golden aura around his head; focused, not grimacing."),
 ('00:05.000', "a medium shot from the side: his palm stays pressed on the mirror, the runes on his bandages glow, and a column of golden light rises inside the mirror, slows, trembles, and stops just below the top rim."),
 ('00:08.000', "a medium shot: <SDZ> lets go and slowly sinks down to one knee in front of the mirror, looking up at it, exhaling. @SDZ{quietly, disappointed}:「……差一点点欸。」"),
 ('00:10.500', "a medium two-shot: <GTS> walks in from the left, pulls him up by the arm with one hand and pats his back. @GTS:「没差啦！下次一定破四千。」"),
], "Crowd murmuring then hushing, a deep rising hum that stalls and wobbles, a long exhale, a hearty back slap.")

seg('06d', 11, 'PLAZA', DAY, "<SQS> tests at the mirror at <LOC>: she draws her sword an inch and frost spreads across the stone; the mirror lights up high and the crowd applauds; she glances back at <LX>.", [
 ('', "A medium shot: <SQS> stands calmly before the mirror, her left hand on the scabbard; she pushes the silver sword out of the scabbard by one inch with her thumb."),
 ('00:02.500', "a low wide shot: a thin layer of white frost spreads across the stone floor around her feet with a crystalline crackle, and the mirror lights up bright and high, almost to the top."),
 ('00:05.500', "a wide shot of the crowd breaking into applause and cheering."),
 ('00:07.000', "a medium shot of <SQS> clicking the sword back into its scabbard without expression, then glancing back over her shoulder toward the student council."),
 ('00:09.000', "a close-up of <LX> in the crowd behind the rope, meeting her eyes calmly."),
], "A crisp metallic slide, crystalline frost crackling, a bright resonant tone, applause and cheers.")

seg('06e', 10, 'PLAZA', DAY, "<YZG> calls <LX>'s name; the crowd murmurs '87' as <LX> calmly walks out toward the mirror while <SQS> watches with concern.", [
 ('', "A medium shot of <YZG> looking down at a list on a clipboard. @YZG:「下一位，林逍。」"),
 ('00:02.500', "a wide shot: heads in the crowd turn; students whisper to each other with amused smiles. Students murmur: <d>[Chinese] 八十七欸……</d>"),
 ('00:05.000', "a medium tracking shot of <LX> walking out of the line toward the mirror, hands relaxed, expression calm."),
 ('00:07.500', "a close-up of <SQS> watching him, her hand tightening slightly on her scabbard."),
], "Crowd whispering and murmuring, footsteps on stone.")

# ---------------- 第 7 场 警报 ----------------
seg('07a', 12, 'PLAZA', DAY, "Just as <LX> raises his hand to the mirror at <LOC>, an alarm bell rings and a crimson pillar of light rises behind the mountain; the mirror flickers strangely and <YSZ> stops his teacup at his lips.", [
 ('', "A medium shot: <LX> stands in front of the mirror and slowly raises his right hand toward the surface."),
 ('00:02.500', "a wide shot: a deep alarm bell tolls across the academy; far behind the halls, a dark crimson pillar of light shoots up into the sky from behind the mountain. The crowd turns, gasping."),
 ('00:05.500', "an insert close-up of the mirror surface right in front of <LX>'s raised hand: it flickers with one strange, dazzling flash of pale gold light, then goes still."),
 ('00:07.500', "a close-up of <YSZ>, his teacup stopping halfway to his lips, his eyes moving from the sky to <LX>."),
 ('00:09.500', "a close-up of <LX> lowering his hand, looking toward the crimson pillar, his face unreadable."),
], "A deep alarm bell tolling repeatedly, a distant rumble, crowd gasping, one sharp shimmering chime.")

seg('07b', 12, 'PLAZA', DAY, "<YZG> orders the teachers to the mountain gate and the students to stay put; <LX> steps down from the stage without testing, and <JYZ> makes a remark.", [
 ('', "A medium shot of <YZG> turning to the teachers, pointing with the ruler. @YZG:「老师们跟我去山门！学生通通待在原地，不准乱跑！」"),
 ('00:04.000', "a wide shot: the teachers, including <WYN> and <GTS>, run off across the plaza after <YZG>, robes and jackets flapping."),
 ('00:06.500', "a medium shot of <LX> stepping down from the mirror's stone platform, hands back in his pockets."),
 ('00:08.500', "a medium shot of <JYZ> by the rope, clicking his tongue. @JYZ:「啧，运气也太好了吧。」"),
], "The alarm bell still tolling, running footsteps, crowd murmuring nervously.")

# ---------------- 第 8 场 夜巡天台 ----------------
seg('08a', 14, 'ROOF', NIGHT, "That night the student council patrols <LOC>: <TXL>'s stream cuts out, <JDB>'s wristband drops dead, and <SDZ> senses something wrong as a faint crimson barrier closes over the rooftop.", [
 ('', "A wide shot: <SQS> leads the student council across <LOC> with a flashlight: <SDZ>, <JDB>, <TXL>, and <LX> walking last; puddles reflect the city lights."),
 ('00:03.000', "a medium close-up of <TXL> frowning at her phone. @TXL:「欸……我直播断线了。」"),
 ('00:05.500', "a close-up of <JDB> tapping his wristband, which has gone completely dark. @JDB:「我的手环也没反应了。」"),
 ('00:08.000', "a medium shot of <SDZ> stopping and looking up, uneasy. @SDZ:「这里怪怪的……好像被什么东西罩住了。」"),
 ('00:11.000', "a wide low-angle shot: a faint translucent dome of dark crimson light finishes closing over the whole rooftop, rippling once."),
], "Night wind, distant city traffic, footsteps splashing through puddles, a phone's disconnect beep, a low humming as the barrier closes.")

seg('08b', 14, 'ROOF', NIGHT, "<MHY> drops down from a water tank onto <LOC> and walks toward the student council; <JDB> is shocked by his realm, and <MHY> states what he wants.", [
 ('', "A wide shot: <MHY> drops lightly from the top of a water tank and lands in a crouch on the wet concrete, then slowly stands, his black coat settling."),
 ('00:03.000', "a medium shot over the student council's shoulders: <MHY> walks slowly toward them, faint crimson qi drifting off his shoulders."),
 ('00:05.500', "a close-up of <JDB>, glasses reflecting crimson light, voice tight. @JDB:「筑……筑基？学生怎么可能是筑基……」"),
 ('00:08.500', "a medium close-up of <MHY> stopping a few meters away, calm and unhurried. @MHY:「我只找一个人，一年前转来的那个。交出来，我就不为难你们。」"),
], "Night wind, a soft landing on wet concrete, slow footsteps, crimson energy humming.")

seg('08c', 12, 'ROOF', NIGHT, "<SQS> steps forward and draws her sword to face <MHY>, telling him he has no right to call out their people, and tells <LX> to take the others away.", [
 ('', "A medium shot: <SQS> steps out in front of the others and draws her silver sword in one smooth motion, frost mist curling off the blade."),
 ('00:02.500', "a close-up of <SQS>, eyes steady on <MHY>. @SQS:「我们天衡的人，轮不到你来点名。」"),
 ('00:06.000', "a medium shot from behind <SQS>, her back to the camera: without turning fully, she tilts her head slightly back. @SQS{quietly}:「林逍，你先带他们走。」"),
 ('00:09.500', "a close-up of <LX> at the back of the group, silent, watching <MHY>."),
], "Night wind, a crisp sword draw, faint frost crackle, crimson energy humming.")

# ---------------- 第 9 场 学生会 vs 墨寒渊 ----------------
seg('09a', 13, 'ROOF', NIGHT, "The student council attacks <MHY> on <LOC> and is overwhelmed: <SDZ> is knocked into a water tank, <TXL>'s talismans burn in midair, and <JDB>'s pills backfire.", [
 ('', "A medium shot: <SDZ> charges at <MHY> with a roar, fist glowing gold; <MHY> meets him with one open palm to the chest and <SDZ> flies backward and slams into a water tank, denting it."),
 ('00:03.500', "a medium shot: <TXL> flings a fan of yellow paper talismans; they fly at <MHY> and every one bursts into crimson flame in midair and falls as ash."),
 ('00:06.500', "a medium shot: <JDB> gulps several pills and lunges forward two steps, then a puff of black smoke bursts from him and he drops to his knees coughing."),
 ('00:09.500', "a wide shot: <SDZ>, <TXL> and <JDB> lie or kneel on the wet concrete; <MHY> stands among them untouched."),
], "A roar, a heavy impact and metal denting, paper flaring into flame, a muffled pop and coughing, night wind.")

seg('09b', 14, 'ROOF', NIGHT, "<SQS> duels <MHY> alone on <LOC>; her sword is knocked away and she is forced to one knee, and <MHY> raises a burning palm.", [
 ('', "A fast medium shot: <SQS> attacks with three quick precise sword strikes, frost trailing; <MHY> blocks each one with his black sword without moving his feet."),
 ('00:03.500', "a close-up: <MHY> twists his blade and the silver sword flies out of <SQS>'s hand, spinning away and clattering on the concrete."),
 ('00:05.000', "a medium shot: a wave of crimson pressure forces <SQS> down onto one knee; she braces a hand on the wet ground, a thin trace of blood at the corner of her lips, still looking up at him."),
 ('00:08.500', "a low-angle medium shot of <MHY> raising his right palm, a crimson flame gathering in it. @MHY:「不说是吧？那我就一个一个问。」"),
 ('00:12.000', "a close-up of a hand in a navy blazer sleeve reaching in from the side of the frame and gripping <MHY>'s gloved wrist firmly."),
], "Rapid sword clashes, a sword clattering on concrete, a heavy pressure hum, a crackling flame, a firm grip.")

seg('09c', 11, 'ROOF', NIGHT, "<LX> holds <MHY>'s wrist; <MHY> recognizes him, and <LX> answers calmly before they separate to face each other.", [
 ('', "A medium two-shot: <LX> stands beside <MHY>, gripping his wrist, completely calm; the crimson flame in <MHY>'s palm sputters and dies."),
 ('00:02.500', "a close-up of <MHY> turning his head to look at <LX>, studying him, then a slow, cold smile. @MHY:「……原来是你啊。」"),
 ('00:06.000', "a close-up of <LX>, eyes natural dark brown, no glow. @LX{low and quiet}:「放开她，我们换个地方。」"),
 ('00:08.500', "a wide shot: <MHY> yanks his wrist free and both men leap back to opposite ends of the rooftop, <MHY> on the left and <LX> on the right, facing each other."),
], "Night wind, a dying flame hiss, two quick jumps and landings on wet concrete.")

# ---------------- 第 12 场 放走 ----------------
seg('12a', 14, 'ROOF', NIGHT, "After the fight, <LX> releases the golden chains; <MHY> lands, asks why he is being let go, receives a message to take back, and vanishes in crimson mist.", [
 ('', "A wide shot: the golden chains binding <MHY> in midair dissolve link by link into golden sparks; he drops and lands on one knee on the wet concrete, panting; <LX> stands a few meters away on the right."),
 ('00:03.500', "a close-up of <MHY>, a faint golden mark around his neck, looking up. @MHY:「……为什么放我走？」"),
 ('00:06.000', "a close-up of <LX>, calm, eyes natural dark brown. @LX:「回去跟派你来的人说，这里没有他要找的东西。」"),
 ('00:10.000', "a medium shot of <MHY> standing, a thin cold smile. @MHY:「你藏不了一辈子的。」 His body dissolves into crimson mist that blows away in the wind."),
], "Chains dissolving with a delicate metallic shimmer, heavy breathing, night wind, mist whooshing away.")

seg('12b', 11, 'ROOF', NIGHT, "<LX> picks up <SQS>'s fallen sword and gently places it beside her hand as she lies semi-conscious; she sees only a blurred figure before passing out.", [
 ('', "A medium shot: the crimson barrier dome over the rooftop cracks and fades away; distant footsteps and voices approach. <LX> walks over and picks up the silver sword from a puddle."),
 ('00:03.500', "a close-up of <LX> crouching and gently laying the sword next to <SQS>'s hand as she lies on her side on the wet concrete."),
 ('00:06.000', "a blurred point-of-view shot from <SQS>'s eyes: the out-of-focus figure of <LX> standing over her, backlit by the city lights; the image wavers and darkens."),
 ('00:08.500', "a close-up of <SQS>'s eyes slowly closing."),
], "Night wind, a crackling barrier fading, distant running footsteps and teachers' voices, a soft metallic clink.")

# ---------------- 第 13 场 医务室 ----------------
seg('13a', 12, 'INFIRM', DAY, "In <LOC>, <YYT> approaches <SDZ> with a long silver needle while he pretends to be asleep.", [
 ('', "A medium shot of <LOC>: <SDZ> lies in a bed with a bandage on his forehead, eyes shut tight; <YYT> walks toward him holding a long silver acupuncture needle."),
 ('00:03.000', "a close-up of <SDZ>'s face: his eyelids flutter and a bead of sweat runs down his temple."),
 ('00:05.000', "a medium shot of <YYT> stopping at the bedside and smiling gently. @YYT:「大壮，你眼皮在抖喔。」"),
 ('00:08.000', "a close-up of <SDZ>, eyes still shut, whispering stiffly. @SDZ:「……我睡着了。」"),
], "Quiet infirmary ambience, birds outside, soft footsteps, a curtain rustling.")

seg('13b', 14, 'INFIRM', DAY, "<SQS> wakes up in <LOC> and immediately asks about <LX>, who is sitting by her bed peeling an apple; <JDB> in the next bed comments.", [
 ('', "A medium shot: <SQS> in a bed with a small bandage on her cheek opens her eyes and sits up abruptly, wincing slightly."),
 ('00:02.500', "a close-up of <SQS>, worried. @SQS:「林逍呢？他有没有怎样？」"),
 ('00:05.000', "a medium shot: <LX> sitting on a stool beside her bed, peeling an apple with a small knife in one long unbroken peel, without looking up. @LX:「我在这。我跑超快的，躲起来了啊。」"),
 ('00:10.000', "a medium shot of <JDB> in the next bed with soot still on his glasses, staring at the ceiling. @JDB:「……你也太扯了吧。」"),
], "Quiet infirmary ambience, an apple being peeled, sheets rustling.")

seg('13c', 13, 'INFIRM', DAY, "<SQS> quietly promises <LX> she will become stronger to protect everyone, including him; he hands her the apple.", [
 ('', "A medium two-shot: <SQS> on the left in the bed, <LX> on the right on the stool; she looks down at her hands, then at him."),
 ('00:02.500', "a close-up of <SQS>, serious and a little shy. @SQS:「我会变更强的。强到可以保护大家……也包括你喔。」"),
 ('00:07.500', "a close-up of <LX> looking at her for a moment, then a faint warm smile. @LX:「嗯，我知道啊。」"),
 ('00:10.500', "a medium shot as he hands her the peeled apple; she takes it, looking away slightly."),
], "Quiet infirmary ambience, birds, sheets rustling.")

# ---------------- 第 14 场 补测 ----------------
seg('14a', 14, 'DUSK', DAY.replace('natural daylight', 'warm orange sunset light'), "At <LOC>, <YZG> makes <LX> take a make-up test; the mirror's light surges for an instant then drops to a tiny glow, and <YZG> sighs and records the number.", [
 ('', "A wide shot of <LOC>: <YZG> stands by the mirror with his clipboard; <LX> walks up across the empty plaza, his long shadow stretching behind him."),
 ('00:03.000', "a medium shot of <YZG>. @YZG:「规矩就是规矩，补测。」"),
 ('00:05.000', "a close-up of <LX>'s palm touching the mirror: the light inside surges up violently for a split second, then instantly drops back down to a tiny faint glow at the very bottom."),
 ('00:07.500', "a close-up of <YZG> squinting at the mirror, as if he saw something, then shaking his head and sighing."),
 ('00:10.000', "an insert of his pen writing on the clipboard paper. @YZG{muttering}:「林逍……八十七。」"),
], "Evening wind, distant crows, a sudden rising hum that cuts off, a pen scratching on paper, a sigh.")

seg('14b', 10, 'EAVES', DAY.replace('natural daylight', 'warm orange sunset light'), "Under the eaves at <LOC>, <YSZ> watches from afar, a leaf frozen above his teacup, and murmurs a line.", [
 ('', "A wide shot under <LOC>: <YSZ> sits alone with a teacup, looking out toward the plaza where small distant figures stand by the mirror."),
 ('00:03.000', "a close-up: a golden ginkgo leaf falls and stops in midair just above his teacup, hanging still."),
 ('00:05.000', "a close-up of <YSZ> smiling faintly, eyes on the distance. @YSZ{softly}:「都一年了，还是这么不老实啊。」"),
], "Evening wind, ginkgo leaves rustling, distant crows.")

# ---------------- 第 15 场 玄冥学院 ----------------
seg('15a', 13, 'HALL', NIGHT, "In <LOC>, <MHY> kneels before <BOSS> and reports.", [
 ('', "An extreme wide shot of <LOC>: <MHY> walks down the long red carpet toward the dark throne and kneels on one knee at its foot, head bowed."),
 ('00:04.000', "a low-angle shot of <BOSS> on the throne in deep shadow, face invisible, one pale finger tapping the armrest. @BOSS:「找到了吗？」"),
 ('00:07.000', "a close-up of <MHY>, a faint golden mark still around his neck, raising his head slowly. @MHY:「天衡学园里……有一个不该存在的人。」"),
 ('00:11.000', "a close-up of the shadowed throne as the crimson lanterns flicker and dim."),
], "A cavernous echoing hall, slow footsteps on stone, lantern flames flickering, a finger tapping wood.")

if __name__ == '__main__':
    jobs = []
    for s in SEG:
        txt, pics = build(s)
        open(f'{HERE}/prompts/{s["id"]}.txt', 'w').write(txt)
        for p in pics: assert os.path.exists(p), p
        jobs.append(dict(id=s['id'], dur=s['dur'], pics=pics))
        last = s['shots'][-1][0]
        assert float(last.split(':')[1]) < s['dur'], s['id']
    json.dump(jobs, open(f'{HERE}/jobs.json', 'w'), indent=1)
    print(len(jobs), 'segments', sum(j['dur'] for j in jobs), 's')
