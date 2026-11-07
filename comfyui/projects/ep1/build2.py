#!/usr/bin/env python3
"""第一集 v2：每个场景挂同一张空景参考图 + 固定布局 + 每个镜头写明机位/站位/朝向/背景"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:1]
import importlib.util
spec = importlib.util.spec_from_file_location('b1', os.path.join(HERE, 'build.py')); b1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b1)
C, STYLE = b1.C, b1.STYLE
SETS = os.path.abspath(os.path.join(HERE, '../sets'))

L = {
 'GATE': (f'{SETS}/SET_gate.png', "the campus entrance shown in <PIC>, on a sunny morning. Fixed layout: in the far background, centered, a grey stone gateway with a dark tiled roof; a grey paved road comes from the gateway straight toward the camera and splits at a small round hedge island with a tall wooden signpost in the center of the frame; the LEFT branch curves away to screen-left, the RIGHT branch curves away to screen-right; tall green trees and lawns line both sides"),
 'OFFICE': (f'{SETS}/SET_office.png', "the student council office shown in <PIC>, morning sunlight. Fixed layout: one long dark wooden table runs straight away from the camera toward the far wall; on the far wall, centered behind the head of the table, a whiteboard with a dark wooden calligraphy plaque above it; the LEFT wall is floor-to-ceiling dark wooden bookshelves with a bonsai; the RIGHT wall has tall dark lattice windows with sunlight coming in; dark wooden chairs with curved backs along both sides of the table. The room never changes"),
 'PLAZA': (f'{SETS}/SET_plaza.png', "the stone test plaza shown in <PIC>, bright daylight. Fixed layout (as seen from the default camera position at the front of the plaza): in the center, the Tianheng Mirror, a tall round bronze mirror on a carved stone pedestal on a round three-step stone platform, its glowing face turned toward the default camera; behind it, the long red-pillared hall with a dark tiled roof and navy banners; on the far LEFT, a big golden ginkgo tree with a wooden armchair and small tea table under it; a red rope line on brass posts curves in front of the platform. The mirror never shows any text, numbers or reflected faces"),
 'DUSK': (f'{SETS}/SET_plaza.png', "the same stone test plaza shown in <PIC>, but at dusk with orange sunset light, long shadows and no crowd. Same fixed layout: the round bronze mirror on its stone platform in the center, the red-pillared hall behind it, the golden ginkgo tree with the armchair on the far left. The mirror never shows any text or numbers"),
 'ROOF': (f'{SETS}/SET_roof.png', "the school rooftop shown in <PIC>, at night. Fixed layout: flat wet concrete with puddles; across the back runs a low concrete parapet with a chain-link fence on top and the glittering city skyline beyond, with one tall lit skyscraper on the left; three small round metal water tanks stand against the parapet left of center"),
 'INFIRM': (f'{SETS}/SET_infirm.png', "the school infirmary shown in <PIC>, warm late-afternoon light. Fixed layout (from the default camera at the door): three white hospital beds in a row along the LEFT side, separated by white curtains, numbered from the camera: bed 1 nearest, bed 2 middle, bed 3 farthest by the window; a big window with sheer curtains on the far wall; a tall dark wooden herb cabinet with many small drawers on the RIGHT wall; a small wooden stool on the right side of bed 2"),
 'EAVES': (f'{SETS}/SET_eaves.png', "the covered corridor shown in <PIC>, at sunset: red pillars, dark tiled eaves, a wooden bench under the eaves with a teapot, a small golden ginkgo tree beside it, and far away across the plaza the round bronze mirror on its pedestal"),
 'HALL': (f'{SETS}/SET_hall.png', "the dark throne hall shown in <PIC>: two rows of black stone pillars hung with dim crimson lanterns, a long red carpet running from the camera straight to a few black steps and a high black throne in deep shadow at the far end"),
}
DAY = b1.DAY; NIGHT = b1.NIGHT
SEG = []
def seg(id, dur, loc, look, summary, stage, shots, sound):
    SEG.append(dict(id=id, dur=dur, loc=loc, look=look, summary=summary, stage=stage, shots=shots, sound=sound))

def build(s):
    if s['id'][:2] in ('05', '06', '07', '04') and '<UNI>' not in s['summary']: s['summary'] += ' All students wear <UNI>.'
    text = s['summary'] + ' ' + s['stage'] + ' ' + ' '.join(t for _, t in s['shots'])
    keys = [k for k in C if '<' + k + '>' in text]
    keys.sort(key=lambda k: text.index('<' + k + '>'))
    num = {k: i + 1 for i, k in enumerate(keys)}; locn = len(keys) + 1
    pics, defs = [], []
    for k in keys:
        d, ps, _ = C[k]
        labels = []
        for p in (ps[:1] if len(keys) > 3 else ps):
            pics.append(p); labels.append(f'<Picture {len(pics)}>')
        defs.append(f'<Subject {num[k]}> is ' + (d.format(p=' and '.join(labels)) if labels else d) + '.')
    simg, stext = L[s['loc']]
    pics.append(simg)
    defs.append(f'<Subject {locn}> is the location: ' + stext.replace('<PIC>', f'<Picture {len(pics)}>') + '.')
    def tok(t):
        for k in keys: t = t.replace('<' + k + '>', f'<Subject {num[k]}>')
        return t.replace('<LOC>', f'<Subject {locn}>')
    defs = [tok(d) for d in defs]
    def sub(t):
        def say(m):
            k, how, line = m.group(1), m.group(2), m.group(3)
            v = C[k][2]; v = v[0].upper() + v[1:]
            return f"{v} (S{num[k]}, in a Taiwanese accent) says{(', ' + how) if how else ''}: <d>[Chinese] {line}</d>"
        return tok(re.sub(r'@(\w+)(?:\{([^}]*)\})?:「([^」]*)」', say, t))
    shots = []
    for i, (tm, t) in enumerate(s['shots']):
        t = sub(t)
        shots.append(f'[Shot {i+1}] {t}' if i == 0 else f'[Shot {i+1}] At {tm}, the shot cuts to {t}')
    ret = []
    for k in keys + ['LOC']:
        lab = f'<Subject {locn}>' if k == 'LOC' else f'<Subject {num[k]}>'
        ins = [f'[Shot {i+1}]' for i, sh in enumerate(shots) if lab in sh] or ['[Shot 1]']
        what = ('the same room/place, layout, props and lighting as the location picture in every shot' if k == 'LOC' else
                'the uniform design stays identical on every student' if k == 'UNI' else 'face, hair, outfit and props stay identical to the reference')
        ret.append(f'{lab} (appears in {", ".join(ins)}): fully_preserved - {what}.')
    out = ("subject_definitions:\n" + '\n'.join(defs) + "\n\nsummary:\n[reference generation] " + sub(s['summary']) +
           "\n\nretention_analysis:\n" + '\n'.join(ret) + "\n\ndetailed_description:\n" + s['look'] + ' ' + STYLE +
           ' Blocking (fixed for the whole video; positions and facing never swap between shots): ' + sub(s['stage']) + '\n' + '\n'.join(shots) +
           "\n\noverall_soundscape:\nNo background music; only diegetic sound and dialogue. " + s['sound'] + "\n\nnon_diegetic_music:\nN/A\n")
    return out, pics

# =========================== 第 2 场 校门 ===========================
GATE_STAGE = "Default camera looks from the fork toward the gateway: the gateway is in the far center background, the signpost island in the middle, the LEFT branch goes off screen-left and the RIGHT branch goes off screen-right."
seg('02a', 11, 'GATE', DAY, "<SDZ> rides an electric scooter with a delivery box in through the gateway of <LOC>, stops by the signpost, checks the glowing wristband on his arm and calls to a classmate.",
 GATE_STAGE + " <SDZ> rides in from the gateway in the center background straight toward the camera and stops just in front of the signpost island, slightly right of center, facing the camera; the square black delivery box is on the back of the scooter the whole time. Other students walk in the background along both branches.", [
 ('', "A wide shot from the default camera position: the gateway in the far center background; <SDZ>, in his navy blazer, rides a small white electric scooter with a square black delivery box on the back out of the gateway, straight down the road toward the camera, and brakes to a stop just right of the signpost island, facing the camera."),
 ('00:03.500', "an insert close-up of his bandaged left forearm on the handlebar, raised slightly: a thin metal spirit-test wristband glows soft blue; the road blurred behind."),
 ('00:05.000', "a medium close-up of <SDZ> on the scooter, facing the camera, the signpost and gateway blurred behind his left shoulder, looking down at the wristband, then exhaling and nodding to himself. @SDZ{under his breath}:「还差五十……今天一定要破四千。」"),
 ('00:08.800', "a medium shot from the default camera direction, the same stone gateway and the wooden signpost island visible behind him exactly as in the location picture (not a park path): still on the scooter in front of the signpost island, he twists around, lifts a takeout bag out of the black delivery box behind him and holds it out toward screen-left with a friendly grin. @SDZ:「欸，你的早餐啦！」"),
], "Morning birds, students chatting, the soft whir and brake squeak of the scooter, a plastic bag rustling.")

seg('02b', 11, 'GATE', DAY, "<JDB> steps out of a silver sports car parked on the right branch of <LOC>, swallows pills from his gourd, watches his wristband flicker, and walks off up the road toward the gateway.",
 GATE_STAGE + " A silver sports car is parked at the curb on the RIGHT branch, its nose pointing toward screen-left; <JDB> gets out of the driver's side facing the camera, stands beside the car on screen-right, then walks screen-left along the road and away toward the gateway.", [
 ('', "A wide shot from the default camera position: a silver sports car parked on the right branch at the right side of the frame, the signpost island and gateway in the center background; the door opens and <JDB>, in his navy blazer and gold round glasses, steps out on the near side of the car, facing the camera, and adjusts his glasses."),
 ('00:03.000', "a medium close-up of <JDB> standing beside the car on screen-right, the gateway blurred behind on screen-left: he tips three small golden pills from his bronze gourd into his palm and tosses them into his mouth, chewing calmly."),
 ('00:05.000', "an insert close-up of the spirit-test wristband on his left wrist: its blue glow flares, flickers weakly, then flares again."),
 ('00:07.000', "a medium close-up of <JDB>, same position, frowning slightly at the wristband and tapping it twice. @JDB{flatly}:「……蛤？这批是不是过期了啊？」 He shrugs, turns to screen-left and walks away up the road toward the gateway."),
], "A sports car engine idling and switching off, a car door, pills rattling in a gourd, a faint electronic flicker, morning crowd chatter.")

seg('02c', 11, 'GATE', DAY, "<TXL> walks down the road from the gateway of <LOC> toward the camera, livestreaming on her phone on a selfie stick.",
 GATE_STAGE + " <TXL> walks out of the gateway down the center of the road toward the camera, holding the selfie stick out in her right hand (screen-left) with the phone facing her; the signpost island is behind her right shoulder as she gets close.", [
 ('', "A wide shot from the default camera position: <TXL> walks out of the gateway in the far center and down the road toward the camera, selfie stick held out, smiling at the phone."),
 ('00:02.000', "a medium close-up of <TXL> walking toward the camera, the gateway blurred in the center background, the phone on the stick at the left edge of the frame. @TXL{cheerfully, chatting}:「哈啰大家早～今天是我们学校的灵测日喔！」"),
 ('00:06.000', "a medium shot of <TXL> stopping in front of the signpost island, facing the camera, glancing at the phone screen, giggling softly at a comment and giving a small wave. @TXL:「礼物多一点，我等一下就冲给你们看～」 The bell on her wrist jingles."),
], "Morning birds, footsteps on pavement, a soft notification chime, the small jingle of a bell, crowd chatter.")

seg('02d', 13, 'GATE', DAY, "<SQS> stops at the fork in <LOC>, studies a campus map and confidently heads down the LEFT branch; <LX> comes from behind and calmly takes the RIGHT branch; she notices, turns around and follows him.",
 GATE_STAGE + " <SQS> stands just in front of the signpost island, facing the camera, holding the map. <LX> walks out of the gateway behind her and passes along the right side of the island. The LEFT branch is the wrong way; the RIGHT branch is the right way.", [
 ('', "A wide shot from the default camera position: <SQS>, in her navy blazer with her sword sheathed at her hip, stands in front of the signpost island facing the camera, holding a folded paper campus map, glancing from the map toward the left branch."),
 ('00:02.500', "a medium close-up of <SQS>, facing the camera, the signpost blurred behind her: she looks at the map, then nods once. @SQS{quietly, to herself}:「应该是……这边吧。」 She turns toward screen-left."),
 ('00:05.500', "a wide shot from the same default position: <SQS> walks a few steps down the LEFT branch toward screen-left; at the same time, in the center background, <LX>, hands in his pockets and his cloth-wrapped sword on his back, walks out of the gateway, passes the right side of the signpost island and turns onto the RIGHT branch toward screen-right without looking at her."),
 ('00:08.500', "a medium shot of <SQS> on the left branch on screen-left, stopping, looking back over her shoulder toward screen-right where <LX> is walking away; she glances at her map, folds it, turns around and follows him toward screen-right a few steps behind him."),
 ('00:11.000', "a medium close-up of <LX> walking toward screen-right on the right branch, trees behind him, eyes forward; the corner of his mouth lifts very slightly."),
], "Morning birds, leaves rustling, a paper map rustling, footsteps on pavement.")

# =========================== 第 3 场 学生会办公室 ===========================
OFF_STAGE = ("<SQS> stands at the head of the table in front of the whiteboard, facing the camera. On the LEFT (bookshelf) side of the table, <TXL> sits in the chair nearest the camera and <JDB> sits in the next chair toward the head. On the RIGHT (window) side, <LX> sits in the chair nearest the camera and <SDZ> sits in the next chair toward the head. "
             "The camera always stays at the foot half of the room, so <TXL> and <JDB> are always on screen-left with bookshelves behind them, <LX> and <SDZ> are always on screen-right with the windows behind them, and <SQS> is always in the center background with the whiteboard behind her. <SQS>'s sword stays sheathed at her hip; <LX> holds a small white teacup.")
seg('03a', 14.5, 'OFFICE', DAY, "A morning meeting in <LOC>: <TXL> reads a forum post about <LX>'s spiritual power, <JDB> asks about it and laughs quietly while <LX> calmly drinks tea.", OFF_STAGE, [
 ('', "A wide shot from the foot of the table, exactly matching the location picture: <SQS> stands at the head of the table in front of the whiteboard looking through a folder; on the left side <TXL> sits nearest the camera with <JDB> beyond her; on the right side <LX> sits in the right foreground nearest the camera holding his teacup and the big <SDZ> sits beyond him further toward the head; <SQS>'s sword hangs sheathed at her hip and her hands hold only the folder."),
 ('00:02.500', "a medium close-up of <TXL> on screen-left, seen from the right side of the table, the bookshelves behind her: she scrolls her phone and looks up with a mischievous little smile toward screen-right. @TXL:「欸，你们看，论坛又在讨论林逍了。」"),
 ('00:05.500', "a medium two-shot of <TXL> and <JDB> on the left side of the table, bookshelves behind them, <JDB> on the right of her in the frame leaning toward her phone and pushing up his glasses. @JDB:「讨论什么？」"),
 ('00:07.000', "a close-up of <TXL>, bookshelves behind her, reading from the screen, trying not to smile. @TXL:「‘转学一年从来没灵测过，他到底几点？’最高赞说……八十七，不能再多了。」"),
 ('00:12.000', "a medium shot of <JDB>, bookshelves behind him, covering his mouth, shoulders shaking with a quiet laugh. @JDB{softly}:「噗……八十七喔。」"),
], "Quiet office ambience, birds outside, a teacup clinking softly, light laughter.")

seg('03b', 14, 'OFFICE', DAY, "Continuing in <LOC>: <SDZ> tries to defend <LX>, <LX> answers mildly, and <SQS> closes her folder to get the meeting back on track.", OFF_STAGE, [
 ('', "A medium two-shot from the foot of the table, angled toward the right (window) side, the lattice windows behind them: <LX> in the right foreground nearest the camera holding his teacup, <SDZ> just beyond him further toward the head of the table; <SDZ> rests a big bandaged hand on <LX>'s shoulder and looks across the table with a slightly awkward, sincere expression. @SDZ:「欸，不要这样啦，人家八十七也是……也是有在努力啊。」"),
 ('00:04.500', "a close-up of <LX>, the lattice windows behind him: unbothered, he takes a slow sip of tea and sets the cup down. @LX{mildly}:「还好啦，我觉得八十七蛮好的。」"),
 ('00:08.000', "a medium-wide shot from the foot of the table, matching the location picture: <TXL> and <JDB> on screen-left, <LX> and <SDZ> on screen-right, <SQS> at the head in front of the whiteboard closing her folder with a firm snap; everyone goes quiet. @SQS{calm but firm}:「好了喔。今天学生会要负责维持秩序，不是在这边聊八卦。」"),
 ('00:12.500', "a medium shot of the left side of the table, bookshelves behind: <TXL> puts her phone face down on the table and <JDB> beside her straightens his glasses and sits up."),
], "Quiet office ambience, a folder snapping shut, a phone set down on wood, then silence.")

seg('03c', 12, 'OFFICE', DAY, "<SQS> walks from the head of the table down the right side to the seated <LX> and quietly tells him to stay behind her during the test; then she leaves through the door at the foot of the room, and <TXL> and <JDB> exchange a look.", OFF_STAGE + " The office door is behind the camera at the foot of the room.", [
 ('', "A medium-wide shot from the foot of the table: <SQS> walks from the head of the table down the right (window) side, passes <SDZ>, and stops beside the seated <LX>, standing on the far side of him, bending slightly toward him; the windows behind them."),
 ('00:02.000', "a close-up of <SQS> bending toward screen-left, the lattice windows behind her, her expression softening a little, speaking quietly. @SQS{quietly}:「等一下测试，你就站我后面，知道吗？」"),
 ('00:05.500', "a close-up of <LX> looking up toward screen-right at her, the windows blurred behind him. @LX{softly}:「……喔，好。」"),
 ('00:07.500', "a medium shot from the head of the table looking back toward the foot: <SQS> straightens up and walks past the camera side toward the door at the foot of the room, her sword still sheathed at her hip; <LX> in his chair watches her go, the faintest smile."),
 ('00:10.000', "a medium two-shot of <TXL> and <JDB> on the left side of the table, bookshelves behind them, slowly turning to exchange a look, eyebrows slightly raised."),
], "Quiet office ambience, footsteps on a wooden floor, a door closing softly.")

# =========================== 第 4 场 灵测开幕 ===========================
PLAZA_STAGE = ("Students in navy uniforms stand in rows behind the red rope line in front of the platform, facing the mirror, so the default camera sees their backs in the foreground. "
               "Teachers stand on the LEFT side of the platform between the mirror and the ginkgo tree; <YSZ> sits in the armchair under the ginkgo tree on the far left. "
               "When a student is tested, they stand on the platform directly in front of the mirror, facing it; side shots of the test are always filmed from the RIGHT side, so the student is on screen-left facing screen-right and the mirror is on screen-right.")
seg('04a', 13, 'PLAZA', DAY, "The opening of Spirit Test Day at <LOC>: <YZG> addresses the whole school from the platform beside the mirror while <WYN> stands behind him.", PLAZA_STAGE + " <YZG> stands on the platform just LEFT of the mirror facing the crowd (facing the camera); <WYN> stands one step behind him to his left with a clipboard.", [
 ('', "An extreme wide high-angle shot from the default camera position behind the crowd, matching the location picture: hundreds of students in rows with their backs to the camera face the mirror; the mirror and platform in the center, the hall behind, the ginkgo tree on the far left; <YZG> stands on the platform left of the mirror."),
 ('00:02.500', "a medium shot from the crowd's side facing the platform: <YZG> stands left of the mirror facing the camera, holding the black wooden ruler behind his back, the glowing mirror on screen-right, <WYN> behind him on screen-left with a clipboard. @YZG:「灵测结果会决定这学期的修炼资源分配。」"),
 ('00:07.000', "a close-up of <YZG>, the mirror's bronze frame blurred on screen-right, the hall behind; he taps the ruler once in his palm. @YZG:「每个人照顺序上来，不准插队，不准作弊，听到没有？」"),
 ('00:11.000', "a reverse wide shot from the platform looking out over the crowd: the rows of students in navy uniforms facing the camera answer in unison, a little half-hearted. Students: <d>[Chinese] 听到了——</d>"),
], "Large outdoor crowd murmuring, banners flapping, a ruler tapping a palm, a crowd answering in unison.")

seg('04b', 14, 'PLAZA', DAY, "<YSZ> sits drinking tea under the ginkgo tree at the left edge of <LOC> as a falling leaf freezes in midair; when the mirror's scanning light passes over him it glitches and goes dark, and <YZG> restarts it.", PLAZA_STAGE + " <YZG> stands on the platform just LEFT of the mirror.", [
 ('', "A medium shot of <YSZ> sitting in the wooden armchair under the golden ginkgo tree at the far left of the plaza, the hall's red pillars behind him, sipping tea calmly; a golden ginkgo leaf drifts down on screen-right of him and stops completely still in midair, hanging there."),
 ('00:03.500', "a wide shot from the default camera position: a soft beam of white light sweeps out from the mirror in the center across the rows of students toward screen-left; as it reaches <YSZ> under the ginkgo tree on the far left, the mirror crackles, flickers and goes completely dark. The crowd falls silent."),
 ('00:07.000', "a close-up of <YSZ> under the ginkgo tree, unhurried, taking another sip, then speaking mildly. @YSZ:「老毛病了，拍一拍就好。」"),
 ('00:10.000', "a medium shot from the crowd's side facing the platform: <YZG>, slightly embarrassed, turns from his spot left of the mirror to the dark mirror on screen-right and gives its bronze frame two firm slaps with his open palm; the mirror lights back up with a soft hum. A few students in the foreground stifle laughs."),
], "Wind in the ginkgo tree, a crackling electric buzz then silence, two hollow metal slaps, a soft hum, muffled giggles.")

# =========================== 第 5 场 同学篇 ===========================
seg('05a', 11, 'PLAZA', DAY, "Waiting in the front row of the crowd at <LOC>, <QTS> casts a fortune on his phone app and announces a bad omen; <JYZ>, standing on his right, brushes it off.", PLAZA_STAGE + " <QTS> and <JYZ> stand side by side in the front row just behind the rope line, facing the platform; in the reverse shots from the platform, <QTS> is on screen-left and <JYZ> is on screen-right, the crowd behind them.", [
 ('', "A medium two-shot from the platform side looking at the front row: <QTS>, under his bucket hat, on screen-left, frowns at the glowing trigram pattern on his phone; <JYZ> stands on screen-right beside him; the red rope in the foreground and rows of uniformed students behind them."),
 ('00:02.500', "a close-up of <QTS> looking up from the phone, completely serious, the crowd blurred behind. @QTS{flatly}:「我刚刚帮学校算了一卦……今天，大凶。」"),
 ('00:06.000', "a medium close-up (not a wide shot) of <JYZ> in his navy crossed-collar uniform with the two swords on his back, on screen-right, the crowd behind him, not even looking over, adjusting the swords on his back. @JYZ:「你算的喔？那就是大吉啦。」 Students behind them chuckle quietly."),
 ('00:09.500', "a close-up of <QTS> looking back down at his phone, unconvinced, tilting his head slightly."),
], "Crowd murmuring, a soft app chime, quiet chuckles.")

seg('05b', 12, 'PLAZA', DAY, "<LXM> stands on the platform at <LOC> and touches the mirror, getting only a faint glow; her cat Yuanbao lazily taps it with a paw and it blazes brightly, leaving the crowd silent.", PLAZA_STAGE + " <LXM> stands on the platform directly in front of the mirror, facing it, with the orange cat on her RIGHT shoulder (the shoulder nearer the camera in the side shots).", [
 ('', "A medium side shot from the right: <LXM> on screen-left in profile facing screen-right, the orange cat on her shoulder, presses her small hand on the mirror on screen-right; a faint, small glow rises at the bottom of the mirror and stays low."),
 ('00:03.500', "a close-up of the orange cat on her shoulder, in the same side view, yawning, then lazily stretching one paw toward screen-right and tapping the mirror surface."),
 ('00:05.500', "a wide shot from the default camera position behind the crowd: the whole mirror in the center suddenly blazes with bright golden light from bottom to top above <LXM>'s small figure on the platform; the rows of students in the foreground go completely still."),
 ('00:08.500', "a close-up of <LXM> in the same side view turning her head to the cat on her shoulder, speaking gently. @LXM:「元宝……你不要乱碰啦。」 The cat blinks slowly."),
], "Crowd murmuring that stops abruptly, a soft hum rising into a bright resonant tone, a cat's small yawn, silence.")

seg('05c', 12, 'PLAZA', DAY, "<FDP>'s mechanical arm malfunctions as he raises it to the mirror at <LOC>; <GTS> steps up from the left side of the platform and catches it with one hand.", PLAZA_STAGE + " <FDP> stands on the platform in front of the mirror facing it, the brass mechanical arm on his RIGHT arm; <GTS> comes from the teachers' spot on the LEFT side of the platform.", [
 ('', "A medium side shot from the right: <FDP> on screen-left facing screen-right raises his brass mechanical arm toward the mirror on screen-right; the arm whirs, sparks and jerks out of control, swinging toward the mirror."),
 ('00:02.500', "a close-up in the same side view: a big hand enters from the far side and catches the brass arm by the wrist one inch from the mirror; <GTS>, who has stepped in on the far side of <FDP>, holds it still with one hand, totally relaxed."),
 ('00:04.500', "a medium two-shot from the crowd's side facing the platform: <GTS> on screen-left still holding the brass arm, <FDP> on screen-right, the mirror behind them; <GTS> smiles at him. @GTS:「小范，下次上来之前，手臂先关机好不好？」"),
 ('00:08.500', "a close-up of <FDP>, same angle, embarrassed, fumbling at a switch on the brass arm. @FDP:「对不起老师……我马上关。」 The arm powers down with a sad whine."),
], "Crowd murmuring, mechanical whirring and sparking, a heavy metal clank when caught, a power-down whine.")

seg('05d', 11, 'PLAZA', DAY, "<JYZ> finishes his test at <LOC>, walks back to the rope line and stops in front of the student council group, making a smug remark; <SQS> ignores him.", PLAZA_STAGE + " The student council group stands in the front row behind the rope line on the RIGHT side of the crowd: <SQS> at the front, <LX> right behind her. <JYZ> walks from the platform to them and stops on their LEFT, facing them.", [
 ('', "A medium side shot from the right: <JYZ> on screen-left takes his hand off the mirror on screen-right as a silver glow fades; he brushes his hair back with satisfaction and steps down off the platform."),
 ('00:03.000', "a medium shot from inside the crowd: <JYZ> on screen-left strolls up to the rope line and stops, turned toward the student council on screen-right: <SQS> at the front, <LX> just behind her shoulder; he glances at them sideways. @JYZ:「学生会也不过就这样嘛。」"),
 ('00:06.500', "a close-up of <JYZ>, facing screen-right, smirking slightly. @JYZ:「明年，会长就是我的了。」"),
 ('00:09.000', "a close-up of <SQS>, facing screen-left past him toward the platform, completely calm, not looking at him; <LX> blurred just behind her."),
], "Crowd murmuring, a fading hum, footsteps on stone.")

# =========================== 第 6 场 学生会篇 ===========================
seg('06a', 11, 'PLAZA', DAY, "<TXL> tests at the mirror at <LOC> while livestreaming; her viewers send gifts and her glow rises a little.", PLAZA_STAGE + " <TXL> stands on the platform in front of the mirror, facing it; her selfie stick is propped in her LEFT hand pointing back at her face; her RIGHT palm stays on the mirror the whole time.", [
 ('', "A medium side shot from the right: <TXL> on screen-left facing screen-right, her right palm on the mirror on screen-right, the phone on the selfie stick held up in her other hand; a modest glow fills the bottom third of the mirror."),
 ('00:02.500', "a close-up of <TXL> in the same side view glancing at the phone. @TXL{softly, to her viewers}:「家人们，帮我一下下～」"),
 ('00:05.000', "an insert of the phone screen filled with floating hearts and small gift icons, chiming rapidly."),
 ('00:06.500', "a medium side shot from the right: her palm still on the mirror, the golden glow inside the mirror visibly climbs from the bottom third up to the middle; <TXL> presses her lips together, eyes lighting up. @TXL{quietly}:「有涨欸……谢谢你们！」"),
], "Crowd murmuring, rapid soft gift chimes, a rising hum, a bell jingling.")

seg('06b', 14, 'PLAZA', DAY, "<JDB> swallows a pill and tests at the mirror at <LOC>; his glow surges then backfires in a puff of black smoke; <HLF>, standing with the teachers on the left side of the platform, praises it in his own way.", PLAZA_STAGE + " <JDB> stands on the platform in front of the mirror facing it; <HLF> stands with the teachers on the LEFT side of the platform.", [
 ('', "A medium side shot from the right: <JDB> on screen-left pops a golden pill into his mouth and places his right palm on the mirror on screen-right; the light inside surges up fast."),
 ('00:03.000', "a close-up in the same side view: a small puff of black smoke bursts from his collar with a muffled pop, soot smudges his glasses, the mirror's light drops back down."),
 ('00:05.000', "a medium shot from the crowd's side facing the platform: <JDB> in front of the mirror, coughing lightly and waving the smoke away with a resigned look."),
 ('00:07.000', "a medium shot of <HLF> standing at the left side of the platform near the ginkgo tree, the hall behind him, clapping and beaming proudly toward screen-right. @HLF:「不错喔！这个炸法，有我当年的味道。」"),
 ('00:10.500', "a close-up of <JDB>, the mirror behind him, wiping his glasses, deadpan, looking toward screen-left at the teacher. @JDB:「老师……这应该不是在称赞吧？」"),
], "Crowd murmuring, a rising hum, a muffled pop, light coughing, clapping, a few laughs.")

seg('06c', 13, 'PLAZA', DAY, "<SDZ> tests at the mirror at <LOC> with everything he has; the light stalls just short of the top, he sinks to one knee disappointed, and <GTS> steps over from the left side of the platform to pull him up.", PLAZA_STAGE + " <SDZ> stands on the platform in front of the mirror facing it, his RIGHT palm on it; <GTS> comes from the teachers' spot on the LEFT side of the platform.", [
 ('', "A wide shot from the default camera position behind the crowd: <SDZ>, in his navy blazer, steps up onto the platform, rolls his shoulders and presses his right palm flat on the mirror. The crowd quiets."),
 ('00:02.500', "a close-up of <SDZ>'s face in a side view from the right, facing screen-right, jaw set, breathing hard through his nose, a vein rising on his temple, a thin golden aura around his head; focused, not grimacing."),
 ('00:05.000', "a medium side shot from the right: <SDZ> on screen-left, his palm stays pressed on the mirror on screen-right, the runes on his bandages glow, and a column of golden light rises inside the mirror, slows, trembles and stops just below the top rim."),
 ('00:08.000', "a medium shot from the crowd's side facing the platform: <SDZ> lets go and slowly sinks down to one knee in front of the mirror, looking up at it, exhaling. @SDZ{quietly, disappointed}:「……差一点点欸。」"),
 ('00:10.500', "the same angle: <GTS> walks in from screen-left, pulls <SDZ> up by the arm with one hand and pats his back; <GTS> on screen-left, <SDZ> on screen-right. @GTS:「没差啦！下次一定破四千。」"),
], "Crowd murmuring then hushing, a deep rising hum that stalls and wobbles, a long exhale, a hearty back slap.")

seg('06d', 11, 'PLAZA', DAY, "<SQS> tests at the mirror at <LOC>: she pushes her sword an inch out of its scabbard and frost spreads over the platform; the mirror lights up high and the crowd applauds; she glances back at <LX> in the front row on the right.", PLAZA_STAGE + " <SQS> stands on the platform in front of the mirror facing it, sword at her LEFT hip; the student council group with <LX> stands in the front row behind the rope line on the RIGHT side of the crowd.", [
 ('', "A medium side shot from the right: <SQS> on screen-left facing the mirror on screen-right, her left hand on the scabbard; she pushes the silver sword one inch out with her thumb."),
 ('00:02.500', "a low wide shot from the crowd's side: a thin layer of white frost spreads across the stone platform around her feet with a crystalline crackle, and the mirror behind her lights up bright and high, almost to the top."),
 ('00:05.500', "a wide shot from the default camera position behind the crowd: the rows of students break into applause."),
 ('00:07.000', "a medium shot from the crowd's side facing the platform: <SQS> clicks the sword back into the scabbard without expression and glances back over her shoulder toward screen-right, toward the front row on the right."),
 ('00:09.000', "a close-up of <LX> standing behind the rope line on the right side of the crowd, the platform blurred behind on screen-left, meeting her eyes calmly."),
], "A crisp metallic slide, crystalline frost crackling, a bright resonant tone, applause and cheers.")

seg('06e', 10, 'PLAZA', DAY, "<YZG>, standing left of the mirror, calls <LX>'s name; the crowd murmurs '87' as <LX> walks out of the front row on the right toward the platform while <SQS> watches with concern.", PLAZA_STAGE + " <YZG> stands on the platform LEFT of the mirror; the student council stands in the front row on the RIGHT side; <LX> walks from there toward screen-left up onto the platform.", [
 ('', "A medium shot from the crowd's side facing the platform: <YZG> on screen-left of the mirror looks down at a list on a clipboard. @YZG:「下一位，林逍。」"),
 ('00:02.500', "a reverse wide shot from the platform looking at the crowd: heads turn; students whisper to each other with amused smiles. Students murmur: <d>[Chinese] 八十七欸……</d>"),
 ('00:05.000', "a medium tracking shot: <LX> steps out of the front row on the right and walks toward screen-left toward the platform, hands relaxed, calm; the mirror ahead of him on screen-left."),
 ('00:07.500', "a close-up of <SQS> standing in the front row behind the rope on the right, watching him walk toward screen-left, her hand tightening slightly on her scabbard."),
], "Crowd whispering and murmuring, footsteps on stone.")

# =========================== 第 7 场 警报 ===========================
seg('07a', 12, 'PLAZA', DAY, "<LX> stands on the platform in front of the mirror at <LOC> and raises his hand; an alarm bell rings and a crimson pillar of light rises behind the hall; the mirror flashes strangely and <YSZ> under the ginkgo tree stops his teacup at his lips.", PLAZA_STAGE + " <LX> stands on the platform in front of the mirror, facing it. The crimson pillar rises far behind the hall, behind the mirror.", [
 ('', "A medium side shot from the right: <LX> on screen-left in profile facing the mirror on screen-right, slowly raising his right hand toward its surface."),
 ('00:02.500', "a wide shot from the default camera position behind the crowd: a deep alarm bell tolls; far behind the hall, behind the mirror, a dark crimson pillar of light shoots up into the sky from beyond the rooftops. The crowd turns its heads up, gasping."),
 ('00:05.500', "an insert close-up from the same right-side angle, <LX>'s raised hand entering from screen-left and the mirror surface filling screen-right (the mirror shows no reflection of anyone): it flickers with one strange, dazzling flash of pale gold light, then goes still."),
 ('00:07.500', "a close-up of <YSZ> in his armchair under the ginkgo tree, his teacup stopping halfway to his lips, his eyes moving from the sky toward screen-right, toward the platform."),
 ('00:09.500', "a close-up of <LX> in the side view, lowering his hand and turning his head to look up behind the mirror at the crimson pillar, his face unreadable."),
], "A deep alarm bell tolling repeatedly, a distant rumble, crowd gasping, one sharp shimmering chime.")

seg('07b', 12, 'PLAZA', DAY, "<YZG> orders the teachers to the mountain gate and the students to stay put; the teachers run off to the left; <LX> steps down from the platform without testing, and <JYZ> in the front row makes a remark.", PLAZA_STAGE + " <YZG> stands LEFT of the mirror; the teachers, including <WYN> and <GTS>, run off past the ginkgo tree to screen-left; <LX> steps down from the platform toward screen-right; <JYZ> stands in the front row behind the rope on the left side.", [
 ('', "A medium shot from the crowd's side facing the platform: <YZG> on screen-left of the mirror turns to the teachers, pointing toward screen-left with the ruler. @YZG:「老师们跟我去山门！学生通通待在原地，不准乱跑！」"),
 ('00:04.000', "a wide shot from the default camera position: <YZG>, <WYN>, <GTS> and the other teachers run off across the plaza toward screen-left past the ginkgo tree, robes and jackets flapping."),
 ('00:06.500', "a medium shot from the crowd's side: <LX> steps down from the platform toward screen-right, hands back in his pockets."),
 ('00:08.500', "a medium close-up of <JYZ>, outdoors on the sunlit stone plaza with the red-pillared hall and other uniformed students behind him (never a studio backdrop), standing in the front row behind the rope on the left, facing screen-right toward <LX>, clicking his tongue. @JYZ:「啧，运气也太好了吧。」"),
], "The alarm bell still tolling, running footsteps, crowd murmuring nervously.")

# =========================== 第 8–9、12 场 天台 ===========================
ROOF_STAGE = ("The camera mostly faces the parapet and skyline. Fixed sides: <MHY> is always on the LEFT side of the rooftop (screen-left, near the water tanks) and the student council is always on the RIGHT side (screen-right). "
              "When the council faces <MHY> they face screen-left; <MHY> faces screen-right.")
seg('08a', 14, 'ROOF', NIGHT + " In this video there is NO villain and no man in a black coat anywhere; only the five students are on the rooftop.", "That night the student council patrols <LOC>; <TXL>'s stream cuts out, <JDB>'s wristband goes dark, <SDZ> senses something wrong, and a faint crimson barrier closes over the rooftop.", "The student council is alone on the rooftop. They walk in from screen-right toward the center in this order from left to right: <SQS> leading with a flashlight, then <SDZ>, <JDB>, <TXL>, and <LX> last on the far right.", [
 ('', "A wide shot facing the parapet and skyline, matching the location picture: the student council walks in from screen-right toward the center across the wet concrete, <SQS> leading with a flashlight, then <SDZ>, <JDB>, <TXL>, and <LX> last; puddles reflect the city lights."),
 ('00:03.000', "a medium close-up of <TXL>, the skyline blurred behind her, frowning at her phone. @TXL:「欸……我直播断线了。」"),
 ('00:05.500', "a close-up of <JDB> tapping his wristband, which has gone completely dark. @JDB:「我的手环也没反应了。」"),
 ('00:08.000', "a medium shot of <SDZ> stopping and looking up, uneasy, the fence and skyline behind him. @SDZ:「这里怪怪的……好像被什么东西罩住了。」"),
 ('00:11.000', "a wide low-angle shot facing the parapet: a faint translucent dome of dark crimson light finishes closing over the whole rooftop, rippling once; the council stands on screen-right looking up."),
], "Night wind, distant city traffic, footsteps splashing through puddles, a phone's disconnect beep, a low humming as the barrier closes.")

seg('08b', 14, 'ROOF', NIGHT, "<MHY> drops from above onto the left side of <LOC> near the water tanks and walks toward the student council on the right; <JDB> is shocked by his realm, and <MHY> states what he wants.", ROOF_STAGE + " The council stands together on the right side facing screen-left: <SQS> in front, <SDZ>, <JDB>, <TXL> beside her, <LX> at the back.", [
 ('', "A wide shot facing the parapet: <MHY> drops from above into the left side of the frame and lands in a crouch on the wet concrete beside the water tanks, then slowly stands, his black coat settling, facing screen-right."),
 ('00:03.000', "a medium over-the-shoulder shot from behind the council on screen-right: <MHY> on screen-left walks slowly toward them across the puddles, faint crimson qi drifting off his shoulders."),
 ('00:05.500', "a close-up of <JDB> facing screen-left, glasses reflecting crimson light, voice tight. @JDB:「筑……筑基？学生怎么可能是筑基……」"),
 ('00:08.500', "a medium close-up of <MHY> facing screen-right, the water tanks and fence behind him, stopping a few meters away, calm and unhurried. @MHY:「我只找一个人，一年前转来的那个。交出来，我就不为难你们。」"),
], "Night wind, a soft landing on wet concrete, slow footsteps, crimson energy humming.")

seg('08c', 12, 'ROOF', NIGHT, "<SQS> steps forward from the group on the right and draws her sword to face <MHY> on the left, then tells <LX>, at the back of the group, to take the others away.", ROOF_STAGE + " <SQS> steps out in front of the group, facing screen-left toward <MHY>; <LX> stands at the back of the group on the far right.", [
 ('', "A medium shot facing the parapet: <SQS> steps out in front of the others toward screen-left and draws her silver sword in one smooth motion, frost mist curling off the blade; <MHY> on the far left."),
 ('00:02.500', "a close-up of <SQS> facing screen-left, eyes steady. @SQS:「我们天衡的人，轮不到你来点名。」"),
 ('00:06.000', "a medium shot from behind <SQS>, her back to the camera on screen-right, <MHY> facing her in the distance on screen-left; without turning fully, she tilts her head slightly toward screen-right. @SQS{quietly}:「林逍，你先带他们走。」"),
 ('00:09.500', "a close-up of <LX> at the back of the group, facing screen-left, silent, watching <MHY>."),
], "Night wind, a crisp sword draw, faint frost crackle, crimson energy humming.")

seg('09a', 13, 'ROOF', NIGHT, "The student council attacks <MHY> on <LOC> and is overwhelmed: <SDZ> is knocked back into the parapet, <TXL>'s talismans burn in midair, and <JDB>'s pills backfire.", ROOF_STAGE, [
 ('', "A medium side shot facing the parapet: <SDZ> charges from screen-right toward <MHY> on screen-left with his fist glowing gold; <MHY> meets him with one open palm to the chest and <SDZ> flies back toward screen-right and slams against the concrete parapet."),
 ('00:03.500', "a medium shot: <TXL> on screen-right flings a fan of yellow paper talismans toward screen-left; every one bursts into crimson flame in midair before reaching <MHY> and falls as ash."),
 ('00:06.500', "a medium shot: <JDB> on screen-right gulps several pills and lunges two steps toward screen-left, then a puff of black smoke bursts from him and he drops to his knees coughing."),
 ('00:09.500', "a wide shot facing the parapet: <SDZ>, <TXL> and <JDB> lie or kneel on the wet concrete on the right side; <MHY> stands untouched on the left."),
], "A heavy impact against concrete, paper flaring into flame, a muffled pop and coughing, night wind.")

seg('09b', 14, 'ROOF', NIGHT, "<SQS> duels <MHY> alone on <LOC>; her sword is knocked away and she is forced to one knee, and <MHY> raises a burning palm over her until a hand grabs his wrist.", ROOF_STAGE + " <SQS> attacks from the right toward screen-left; after she falls she kneels on the right with <MHY> standing over her on the left.", [
 ('', "A fast medium side shot facing the parapet: <SQS> on screen-right attacks <MHY> on screen-left with three quick sword strikes, frost trailing; <MHY> blocks each one with his black sword without moving his feet."),
 ('00:03.500', "a close-up: <MHY> twists his blade and the silver sword flies out of <SQS>'s hand toward screen-right, spinning away and clattering on the concrete."),
 ('00:05.000', "a medium shot: a wave of crimson pressure forces <SQS> down onto one knee on screen-right; she braces a hand on the wet ground, a thin trace of blood at the corner of her lips, still looking up toward screen-left at him."),
 ('00:08.500', "a low-angle medium shot of <MHY> on screen-left facing screen-right, raising his right palm, a crimson flame gathering in it. @MHY:「不说是吧？那我就一个一个问。」"),
 ('00:12.000', "a close-up of <MHY>'s raised gloved wrist: a hand in a navy blazer sleeve reaches in from the right edge of the frame and grips it firmly."),
], "Rapid sword clashes, a sword clattering on concrete, a heavy pressure hum, a crackling flame, a firm grip.")

seg('09c', 11, 'ROOF', NIGHT, "<LX> holds <MHY>'s wrist; <MHY> recognizes him, <LX> answers calmly, and they leap apart to the two ends of the rooftop: <MHY> on the left, <LX> on the right.", ROOF_STAGE + " <LX> stands on the RIGHT of <MHY>, gripping his wrist; after they jump apart, <MHY> is on the far left and <LX> on the far right, facing each other.", [
 ('', "A medium two-shot facing the parapet: <MHY> on screen-left, <LX> on screen-right gripping his raised wrist, completely calm; the crimson flame in <MHY>'s palm sputters and dies."),
 ('00:02.500', "a close-up of <MHY> turning his head toward screen-right to look at <LX>, studying him, then a slow, cold smile. @MHY:「……原来是你啊。」"),
 ('00:06.000', "a close-up of <LX> facing screen-left, eyes natural dark brown with no glow. @LX{low and quiet}:「放开她，我们换个地方。」"),
 ('00:08.500', "a wide shot facing the parapet: <MHY> yanks his wrist free and both men leap back, <MHY> to the far left near the water tanks and <LX> to the far right, landing and facing each other."),
], "Night wind, a dying flame hiss, two quick jumps and landings on wet concrete.")

seg('12a', 14, 'ROOF', NIGHT, "After the fight, <LX> on the right releases the golden chains; <MHY> drops on the left, asks why he is being let go, receives a message to take back, and vanishes in crimson mist.", ROOF_STAGE, [
 ('', "A wide shot facing the parapet: on the left, golden chains binding <MHY> in midair dissolve link by link into golden sparks; he drops and lands on one knee on the wet concrete, panting; <LX> stands a few meters away on the right, facing screen-left."),
 ('00:03.500', "a close-up of <MHY> facing screen-right, a faint golden mark around his neck, looking up. @MHY:「……为什么放我走？」"),
 ('00:06.000', "a close-up of <LX> facing screen-left, calm, eyes natural dark brown. @LX:「回去跟派你来的人说，这里没有他要找的东西。」"),
 ('00:10.000', "a medium shot of <MHY> on screen-left standing up, facing screen-right, a thin cold smile. @MHY:「你藏不了一辈子的。」 His body dissolves into crimson mist that blows away to screen-left."),
], "Chains dissolving with a delicate metallic shimmer, heavy breathing, night wind, mist whooshing away.")

seg('12b', 11, 'ROOF', NIGHT, "<LX> picks up <SQS>'s fallen sword on the right side of <LOC> and lays it beside her hand as she lies semi-conscious; she sees only his blurred figure before passing out.", ROOF_STAGE + " <SQS> lies on her side on the right side of the rooftop, her head toward screen-left; her sword lies in a puddle a few meters to screen-right of her.", [
 ('', "A medium shot facing the parapet: the crimson barrier dome over the rooftop cracks and fades away; <LX> walks toward screen-right and picks up the silver sword from a puddle."),
 ('00:03.500', "a close-up of <LX> crouching beside <SQS> and gently laying the sword next to her hand on the wet concrete."),
 ('00:06.000', "a blurred point-of-view shot from <SQS>'s eyes looking up: the out-of-focus figure of <LX> standing over her, backlit by the city lights; the image wavers and darkens."),
 ('00:08.500', "a close-up of <SQS>'s face on the wet concrete, her eyes slowly closing."),
], "Night wind, a crackling barrier fading, distant running footsteps and teachers' voices, a soft metallic clink.")

# =========================== 第 13 场 医务室 ===========================
INF_STAGE = ("<SDZ> lies in bed 1 (nearest the camera), <SQS> lies in bed 2 (middle), <JDB> lies in bed 3 (farthest, by the window). <LX> sits on the wooden stool on the RIGHT side of bed 2. "
             "From the default camera at the door, the beds are on screen-left with their heads against the left wall, and the herb cabinet is on screen-right.")
seg('13a', 12, 'INFIRM', DAY, "In <LOC>, <YYT> walks from the herb cabinet on the right to bed 1 with a long silver needle while <SDZ> pretends to be asleep.", INF_STAGE + " <YYT> starts at the herb cabinet on the right and walks to the right side of bed 1.", [
 ('', "A wide shot from the default camera at the door, matching the location picture: <SDZ> lies in bed 1 on screen-left with a bandage on his forehead, eyes shut tight; <YYT> turns from the herb cabinet on screen-right and walks toward his bed holding a long silver acupuncture needle."),
 ('00:03.000', "a close-up of <SDZ>'s face on the pillow: his eyelids flutter and a bead of sweat runs down his temple."),
 ('00:05.000', "a medium shot of <YYT> stopping on the right side of bed 1, looking down at him, smiling gently. @YYT:「大壮，你眼皮在抖喔。」"),
 ('00:08.000', "a close-up of <SDZ>, eyes still shut, whispering stiffly. @SDZ:「……我睡着了。」"),
], "Quiet infirmary ambience, birds outside, soft footsteps, a curtain rustling.")

seg('13b', 14, 'INFIRM', DAY, "<SQS> wakes up in bed 2 of <LOC> and immediately asks about <LX>, who sits on the stool on the right side of her bed peeling an apple; <JDB> in bed 3 comments.", INF_STAGE, [
 ('', "A medium shot of bed 2: <SQS>, with a small bandage on her cheek, opens her eyes and sits up abruptly, wincing slightly; the window behind."),
 ('00:02.500', "a close-up of <SQS> sitting up in bed, facing screen-right, worried. @SQS:「林逍呢？他有没有怎样？」"),
 ('00:05.000', "a medium shot of <LX> on the stool on the right side of bed 2, facing screen-left toward her, peeling an apple with a small knife in one long unbroken peel, without looking up. @LX:「我在这。我跑超快的，躲起来了啊。」"),
 ('00:10.000', "a medium shot of <JDB> in bed 3 by the window, soot still on his glasses, staring at the ceiling. @JDB:「……你也太扯了吧。」"),
], "Quiet infirmary ambience, an apple being peeled, sheets rustling.")

seg('13c', 13, 'INFIRM', DAY, "<SQS>, sitting up in bed 2, quietly promises <LX> she will become stronger to protect everyone including him; he hands her the apple.", INF_STAGE + " In the two-shot <SQS> in bed is on screen-left and <LX> on the stool is on screen-right.", [
 ('', "A medium two-shot: <SQS> sitting up in bed 2 on screen-left, <LX> on the stool on screen-right facing her; she looks down at her hands, then at him."),
 ('00:02.500', "a close-up of <SQS> facing screen-right, serious and a little shy. @SQS:「我会变更强的。强到可以保护大家……也包括你喔。」"),
 ('00:07.500', "a close-up of <LX> facing screen-left, looking at her for a moment, then a faint warm smile. @LX:「嗯，我知道啊。」"),
 ('00:10.500', "the medium two-shot again: he hands her the peeled apple toward screen-left; she takes it, looking away slightly."),
], "Quiet infirmary ambience, birds, sheets rustling.")

# =========================== 第 14 场 补测 ===========================
DUSKLOOK = DAY.replace('natural daylight', 'warm orange sunset light')
seg('14a', 14, 'DUSK', DUSKLOOK, "At the empty <LOC>, <YZG> makes <LX> take a make-up test; the mirror's light surges for an instant then drops to a tiny glow, and <YZG> sighs and records it.", "<YZG> stands on the platform LEFT of the mirror with a clipboard; <LX> walks across the empty plaza from the front toward the platform and stands in front of the mirror, facing it. Side shots are filmed from the RIGHT: <LX> on screen-left, mirror on screen-right.", [
 ('', "A wide shot from the default camera position, matching the location picture but at sunset and empty: <YZG> stands on the platform left of the mirror; <LX> walks across the plaza toward the platform, his long shadow stretching behind him."),
 ('00:03.000', "a medium shot of <YZG> left of the mirror, facing the camera, the hall behind him. @YZG:「规矩就是规矩，补测。」"),
 ('00:05.000', "a close-up in a side view from the right: <LX>'s palm on screen-left touches the mirror on screen-right; the light inside surges up violently for a split second, then instantly drops back down to a tiny faint glow at the very bottom."),
 ('00:07.500', "a close-up of <YZG> squinting at the mirror toward screen-right, as if he saw something, then shaking his head and sighing."),
 ('00:10.000', "an insert of his pen writing on the clipboard paper. @YZG{muttering}:「林逍……八十七。」"),
], "Evening wind, distant crows, a sudden rising hum that cuts off, a pen scratching on paper, a sigh.")

seg('14b', 10, 'EAVES', DUSKLOOK, "Under the eaves at <LOC>, <YSZ> watches the plaza from afar, a leaf frozen above his teacup, and murmurs a line.", "<YSZ> sits on the wooden bench under the eaves on the LEFT, facing screen-right toward the distant plaza and mirror.", [
 ('', "A wide shot matching the location picture: <YSZ> sits alone on the bench under the eaves on screen-left with a teacup, looking toward screen-right where small distant figures stand by the mirror across the plaza."),
 ('00:03.000', "a close-up: a golden ginkgo leaf falls and stops in midair just above his teacup, hanging still."),
 ('00:05.000', "a close-up of <YSZ> facing screen-right, smiling faintly, eyes on the distance. @YSZ{softly}:「都一年了，还是这么不老实啊。」"),
], "Evening wind, ginkgo leaves rustling, distant crows.")

# =========================== 第 15 场 玄冥大殿 ===========================
seg('15a', 13, 'HALL', NIGHT, "In <LOC>, <MHY> walks down the red carpet and kneels before <BOSS> on the throne, and reports.", "<MHY> walks away from the camera down the center of the red carpet and kneels at the foot of the steps facing the throne; <BOSS> sits on the throne at the far end.", [
 ('', "An extreme wide shot matching the location picture: <MHY>, his back to the camera, walks down the center of the long red carpet toward the dark throne and kneels on one knee at the foot of the steps, head bowed."),
 ('00:04.000', "a low-angle shot of <BOSS> on the throne in deep shadow, face invisible, one pale finger tapping the armrest. @BOSS:「找到了吗？」"),
 ('00:07.000', "a close-up of <MHY> kneeling, seen from in front (from the throne side), a faint golden mark still around his neck, raising his head slowly. @MHY:「天衡学园里……有一个不该存在的人。」"),
 ('00:11.000', "a close-up of the shadowed throne as the crimson lanterns flicker and dim."),
], "A cavernous echoing hall, slow footsteps on stone, lantern flames flickering, a finger tapping wood.")

if __name__ == '__main__':
    os.makedirs(f'{HERE}/prompts2', exist_ok=True)
    jobs = []
    for s in SEG:
        txt, pics = build(s)
        assert not re.search(r'<[A-Z]{2,}>', txt), (s['id'], re.findall(r'<[A-Z]{2,}>', txt))
        open(f'{HERE}/prompts2/{s["id"]}.txt', 'w').write(txt)
        for p in pics: assert os.path.exists(p), p
        jobs.append(dict(id=s['id'], dur=s['dur'], pics=pics))
    json.dump(jobs, open(f'{HERE}/jobs2.json', 'w'), indent=1)
    print(len(jobs), 'segments', sum(j['dur'] for j in jobs), 's', 'max pics', max(len(j['pics']) for j in jobs))
