"""GeoMaster 3D — AI-supported assessment demonstration.
Run: streamlit run app.py
Dependencies: streamlit, plotly
"""
import math
import time
from collections import Counter

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="GeoMaster 3D | Assessment Lab", page_icon="🧊", layout="wide", initial_sidebar_state="collapsed")

# The 10 questions are intentionally fixed so that the answer key,
# feedback samples, and teacher review are reproducible.
QUESTIONS = [
    dict(level="Easy", shape="Cube", topic="Properties of solids",
         question="How many faces does a cube have?", options=["4", "6", "8", "12"], answer="6",
         hints=["Think about the top, bottom, and four sides.", "Every face of a cube is a square."],
         explanation="A cube has six square faces: top, bottom, front, back, left, and right.",
         wrong="Distinguish faces (flat surfaces) from edges and vertices."),
    dict(level="Easy", shape="Cuboid", topic="Volume of prisms",
         question="A rectangular prism is 3 cm long, 4 cm wide, and 5 cm high. What is its volume?",
         options=["12 cm³", "47 cm³", "60 cm³", "94 cm³"], answer="60 cm³",
         hints=["Volume = length × width × height.", "Compute 3 × 4 × 5."],
         explanation="V = l × w × h = 3 × 4 × 5 = 60 cm³.",
         wrong="For a rectangular prism, multiply all three dimensions; the unit is cubic."),
    dict(level="Easy", shape="Sphere", topic="Radius and diameter",
         question="A sphere has a radius of 7 cm. What is its diameter?",
         options=["3.5 cm", "7 cm", "14 cm", "49 cm"], answer="14 cm",
         hints=["The diameter passes through the sphere's center.", "Diameter = 2 × radius."],
         explanation="d = 2r = 2 × 7 = 14 cm.",
         wrong="Remember that diameter is twice the radius, not the square of it."),
    dict(level="Medium", shape="Cube", topic="Surface area",
         question="Find the total surface area of a cube with side length 4 cm.",
         options=["16 cm²", "64 cm²", "96 cm²", "128 cm²"], answer="96 cm²",
         hints=["There are six congruent square faces.", "Use SA = 6a² and a = 4."],
         explanation="SA = 6a² = 6 × 4² = 6 × 16 = 96 cm².",
         wrong="Calculate the area of one face and multiply by six; use square units."),
    dict(level="Medium", shape="Cylinder", topic="Cylinder volume",
         question="A cylinder has radius 3 cm and height 8 cm. What is its exact volume?",
         options=["24π cm³", "48π cm³", "72π cm³", "144π cm³"], answer="72π cm³",
         hints=["Volume = area of circular base × height.", "Use V = πr²h = π × 3² × 8."],
         explanation="V = πr²h = π × 9 × 8 = 72π cm³.",
         wrong="Square the radius, not the height; then multiply by π and the height."),
    dict(level="Medium", shape="Cone", topic="Cone volume",
         question="A cone has radius 3 cm and height 12 cm. What is its exact volume?",
         options=["36π cm³", "72π cm³", "108π cm³", "324π cm³"], answer="36π cm³",
         hints=["A cone is one-third of the matching cylinder.", "Use V = (1/3)πr²h."],
         explanation="V = (1/3)π × 3² × 12 = (1/3) × 108π = 36π cm³.",
         wrong="Do not forget the factor of one-third in the cone-volume formula."),
    dict(level="Medium", shape="Cuboid", topic="Space diagonal",
         question="A rectangular prism measures 3 cm × 4 cm × 12 cm. Find its space diagonal.",
         options=["7 cm", "12 cm", "13 cm", "19 cm"], answer="13 cm",
         hints=["Use the 3D Pythagorean theorem.", "Compute √(3² + 4² + 12²)."],
         explanation="d = √(l² + w² + h²) = √(9 + 16 + 144) = √169 = 13 cm.",
         wrong="Use the squares of all three dimensions before taking the square root."),
    dict(level="Hard", shape="Sphere", topic="Sphere surface area",
         question="Find the exact surface area of a sphere with radius 6 cm.",
         options=["36π cm²", "72π cm²", "144π cm²", "288π cm²"], answer="144π cm²",
         hints=["The sphere's surface-area formula involves r².", "Use SA = 4πr² = 4π × 6²."],
         explanation="SA = 4πr² = 4π × 36 = 144π cm².",
         wrong="Use 4πr² for a sphere's surface area, not the volume formula."),
    dict(level="Hard", shape="Square Pyramid", topic="Pyramid volume",
         question="A square pyramid has a base side length of 6 cm and vertical height of 9 cm. Find its volume.",
         options=["54 cm³", "108 cm³", "162 cm³", "324 cm³"], answer="108 cm³",
         hints=["The base is a square with area a².", "Use V = (1/3) × 6² × 9."],
         explanation="V = (1/3)Bh = (1/3) × 36 × 9 = 108 cm³.",
         wrong="First find the square base's area, then multiply by height and divide by three."),
    dict(level="Hard", shape="Sphere", topic="Similarity and scaling",
         question="The radius of a sphere is doubled. By what factor does its volume increase?",
         options=["2", "4", "6", "8"], answer="8",
         hints=["Volume is proportional to the third power of the radius.", "Compare (2r)³ with r³."],
         explanation="Volume is proportional to r³; doubling the radius multiplies volume by 2³ = 8.",
         wrong="Volume scales cubically: a scale factor of k produces a volume factor k³."),
]
assert len(QUESTIONS) == 10
assert Counter(q['level'] for q in QUESTIONS) == {'Easy': 3, 'Medium': 4, 'Hard': 3}
assert all(len(q['options']) == 4 and q['answer'] in q['options'] for q in QUESTIONS)

# Reproducible examples of *draft* AI feedback and teacher review.
SAMPLES = [
    dict(title="Strong understanding", answer="The formula is V = s³. With s = 5 cm, V = 5³ = 125 cm³.",
         draft="Excellent! This is correct.",
         reviewed="Excellent work. You chose the cube-volume formula, substituted the side length correctly, and wrote the correct unit (cm³). Keep presenting the formula and units clearly.",
         changed="Made the praise specific to the method, substitution, and units."),
    dict(title="Developing understanding", answer="5 × 5 × 5 = 125",
         draft="Good answer. Add more explanation.",
         reviewed="Your multiplication is correct: 5 × 5 × 5 = 125. To make the solution complete, introduce the formula V = s³ and state the answer as 125 cm³ because volume is measured in cubic units.",
         changed="Identified precisely which two parts were missing: formula and units."),
    dict(title="Needs support", answer="5 × 5 = 25 cm².",
         draft="Incorrect. Review the volume formula.",
         reviewed="You correctly found the area of one square face (25 cm²), but the question asks for volume. Multiply by the third side: 5 × 5 × 5 = 125 cm³. Try another cube-volume problem using V = s³.",
         changed="Explained the misconception, gave a worked correction, and added a constructive next step."),
]

PROMPTS = [
    ("Prompt 1 · Generate the mathematics quiz",
     "Create exactly 10 accurate multiple-choice questions about 3D geometry for secondary-school students: 3 easy, 4 medium, and 3 hard. Include a range of solid shapes and topics, with four distinct answer options and one correct answer per question. Provide two progressive hints, a verified answer key, a step-by-step explanation, and a common misconception to review for each question. Make harder questions require reasoning, not simply identifying a shape."),
    ("Prompt 2 · Build the interactive website",
     "Develop a responsive Streamlit assessment website named GeoMaster 3D using the verified 10-question quiz. Use a modern teal-and-navy interface with accessible contrast and large buttons. Add a quiz timer, progressive hints, a choice between immediate correctness checking and checking answers at the end, and a final answer-key review. Keep the difficulty progression Easy (3), Medium (4), then Hard (3). Include an interactive 3D model and a results dashboard."),
    ("Prompt 3 · Draft feedback for teacher review",
     "For the question 'A cube has a side length of 5 cm. Find its volume', review three sample student responses showing strong, developing, and weak understanding. Draft brief, constructive formative feedback for each. Identify what is correct, explain mistakes and missing units, and recommend one next step. Keep the initial AI feedback separate from teacher-reviewed revisions, and make it possible to document what the teacher changed. Do not claim that rule-based quiz feedback is generated by a live AI model."),
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*='css'], .stApp {font-family:'DM Sans',sans-serif;}
.stApp {background: #f3f8f8; color:#173542;}
.block-container {max-width:1100px;padding-top:1.4rem;padding-bottom:4rem;}
h1,h2,h3,h4,p, label {color:#173542;}
h1 {letter-spacing:-.045em;font-weight:800;}
[data-testid='stHeader'] {background:transparent;}
header[data-testid='stHeader'] {height:2rem;}
.card {background:white;border:1px solid #dce8e9;border-radius:18px;padding:24px;margin:8px 0 18px;box-shadow:0 8px 22px rgba(19,58,68,.04);}
.hero {background:linear-gradient(116deg,#123849,#146a75 60%,#16a79a);border-radius:22px;padding:34px 36px;margin-bottom:20px;color:white;}
.hero h1 {color:white;margin:.2rem 0;font-size:clamp(2.1rem,4vw,3.5rem);}
.hero p {color:#d4f9f3;font-size:1.03rem;margin-bottom:0;}
.eyebrow {font-size:.76rem;font-weight:800;letter-spacing:.14em;color:#9df4d9;}
.level {color:#007c75;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;}
.stat {background:white;border:1px solid #dce8e9;border-radius:14px;padding:14px;text-align:center;}
.stat strong {font-size:1.7rem;color:#075e65;display:block;}
.stat span {font-size:.82rem;color:#69808a;}
.stButton>button[kind='primary'], .stFormSubmitButton>button[kind='primary'] {background:#087b75;color:white;border:0;border-radius:11px;font-weight:750;min-height:46px;}
.stButton>button, .stFormSubmitButton>button {border-radius:11px;font-weight:700;min-height:42px;}
[data-testid='stRadio'] {background:white;border:1px solid #dce8e9;padding:15px 19px;border-radius:14px;}
[data-testid='stAlert'] {border-radius:12px;}
[data-testid='stMetric'] {background:white;padding:12px 15px;border-radius:15px;border:1px solid #dce8e9;}
div[data-testid='stProgress']>div {background:#cfece6;}
[data-testid='stTabs'] button {font-weight:700;}
.smallnote {font-size:.85rem;color:#68808c;}
@media(max-width:600px){.hero{padding:22px 18px}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)


def solid_plot(shape):
    """Simple touch-rotatable Plotly 3D model for geometry orientation."""
    fig = go.Figure()
    if shape in {"Cube", "Cuboid", "Square Pyramid"}:
        if shape == "Square Pyramid":
            verts = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(0,0,1.4)]
            tri = [(0,2,1),(0,3,2),(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
        else:
            a,b,c=(1,1,1) if shape=="Cube" else (1.5,.8,1)
            verts=[(-a,-b,-c),(a,-b,-c),(a,b,-c),(-a,b,-c),(-a,-b,c),(a,-b,c),(a,b,c),(-a,b,c)]
            tri=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
        x,y,z=zip(*verts)
        i,j,k=zip(*tri)
        fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color='#26a9aa',opacity=.9,flatshading=True,hoverinfo='skip'))
        # Draw crisp silhouette/edges.
        edges=set()
        if shape == 'Square Pyramid':
            edges={(0,1),(1,2),(2,3),(0,3),(0,4),(1,4),(2,4),(3,4)}
        else:
            edges={(0,1),(1,2),(2,3),(0,3),(4,5),(5,6),(6,7),(4,7),(0,4),(1,5),(2,6),(3,7)}
        ex,ey,ez=[],[],[]
        for a,b in sorted(edges):
            ex.extend([verts[a][0],verts[b][0],None]); ey.extend([verts[a][1],verts[b][1],None]); ez.extend([verts[a][2],verts[b][2],None])
        fig.add_trace(go.Scatter3d(x=ex,y=ey,z=ez,mode='lines',line=dict(color='#073f50',width=5),hoverinfo='skip'))
    else:
        n=32
        if shape == 'Sphere':
            xs,ys,zs=[],[],[]
            for t in range(19):
                theta=math.pi*t/18
                for p in range(n+1):
                    phi=2*math.pi*p/n
                    xs.append(math.sin(theta)*math.cos(phi))
                    ys.append(math.sin(theta)*math.sin(phi))
                    zs.append(math.cos(theta))
            ii,jj,kk=[],[],[]
            for t in range(18):
                for p in range(n):
                    q=t*(n+1)+p
                    ii.extend([q,q+1]);jj.extend([q+1,q+n+2]);kk.extend([q+n+1,q+n+1])
            fig.add_trace(go.Mesh3d(x=xs,y=ys,z=zs,i=ii,j=jj,k=kk,color='#26a9aa',opacity=.9,hoverinfo='skip'))
        else:
            radius=1.0; zs=[-1,1]
            verts=[]
            if shape == 'Cone':
                verts=[(math.cos(2*math.pi*p/n),math.sin(2*math.pi*p/n),-1) for p in range(n)]
                verts.extend([(0,0,1.45),(0,0,-1)])
                tri=[(p,(p+1)%n,n) for p in range(n)]+[(n+1,(p+1)%n,p) for p in range(n)]
            else:
                verts=[(math.cos(2*math.pi*p/n),math.sin(2*math.pi*p/n),z) for z in zs for p in range(n)]
                verts.extend([(0,0,-1),(0,0,1)])
                tri=[]
                for p in range(n):
                    q=(p+1)%n
                    tri.extend([(p,q,n+q),(p,n+q,n+p),(2*n,q,p),(2*n+1,n+p,n+q)])
            x,y,z=zip(*verts);i,j,k=zip(*tri)
            fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,color='#26a9aa',opacity=.9,hoverinfo='skip'))
    fig.update_layout(height=290,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor='rgba(0,0,0,0)',showlegend=False,
                      scene=dict(bgcolor='rgba(0,0,0,0)',xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),
                                 aspectmode='cube',camera=dict(eye=dict(x=1.6,y=1.5,z=1.2))))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False,'scrollZoom':True},key=f"shape_{st.session_state.cursor}_{shape}")


def initialize():
    defaults={'screen':'welcome','cursor':0,'answers':{},'hint_counts':{},'mode':'Check at the end',
              'started':None,'ended':None,'feedback_text':'','notes':'','reflection':''}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v


def restart():
    for key in list(st.session_state.keys()):
        if key.startswith('choice_'):
            del st.session_state[key]
    for key in ('cursor','answers','hint_counts','started','ended'):
        st.session_state[key]={'cursor':0,'answers':{},'hint_counts':{},'started':None,'ended':None}[key]
    st.session_state.screen='welcome'


def elapsed():
    start=st.session_state.started
    if start is None:return '00:00'
    end=st.session_state.ended or time.time()
    seconds=max(0,int(end-start))
    return f'{seconds//60:02d}:{seconds%60:02d}'


def go_to_next():
    if st.session_state.cursor==9:
        st.session_state.ended=time.time()
        st.session_state.screen='results'
    else:
        st.session_state.cursor+=1
    st.rerun()


def result_summary():
    correct=[idx for idx,choice in st.session_state.answers.items() if choice==QUESTIONS[idx]['answer']]
    incorrect=[idx for idx,choice in st.session_state.answers.items() if choice!=QUESTIONS[idx]['answer']]
    blank=[i for i in range(10) if i not in st.session_state.answers]
    return correct,incorrect,blank


def feedback_for_results():
    correct,incorrect,blank=result_summary()
    if len(correct)==10:
        return ['Excellent work: all 10 answers are correct! Try extending your learning to composite solids and multi-step proof problems.']
    if len(blank)>7:
        return ['Most questions were left unanswered. Review the basic 3D shape properties and core volume/area formulas, then attempt the quiz again.']
    items=[]
    if incorrect:
        items.append('Your next steps are based on the questions you missed:')
        for idx in incorrect:
            q=QUESTIONS[idx]
            items.append(f"Question {idx+1} · {q['topic']}: {q['wrong']}")
    if blank:
        items.append(f"You skipped {len(blank)} question(s): {', '.join(str(i+1) for i in blank)}. Practice these topics before your next attempt.")
    if not incorrect and blank:
        items.insert(0,'All answered questions were correct. Complete the remaining questions to demonstrate full understanding.')
    return items

initialize()

st.markdown('<div style="font-weight:800;font-size:1.15rem;color:#12666c;margin-bottom:.5rem">◈ GeoMaster <span style="color:#1b9f91">3D</span> <span style="font-size:.8rem;color:#80949a;font-weight:600">/ Assessment Lab</span></div>',unsafe_allow_html=True)

# Site navigation is deliberately simple and always accessible.
nav1,nav2,nav3,nav4=st.columns(4)
with nav1:
    if st.button('🏠 Home',use_container_width=True): st.session_state.screen='welcome';st.rerun()
with nav2:
    if st.button('🧩 Quiz',use_container_width=True):
        if st.session_state.started is None: st.session_state.started=time.time()
        st.session_state.screen='quiz';st.rerun()
with nav3:
    if st.button('💬 Feedback samples',use_container_width=True): st.session_state.screen='samples';st.rerun()
with nav4:
    if st.button('📚 Prompts & Reflection',use_container_width=True): st.session_state.screen='documentation';st.rerun()

if st.session_state.screen=='welcome':
    st.markdown('''<div class="hero"><div class="eyebrow">AI-SUPPORTED MATHEMATICS ASSESSMENT</div>
    <h1>Geometry you can explore.</h1><p>10 verified questions. Three levels. Clear feedback.<br>Understand 3D geometry, one challenge at a time.</p></div>''',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for col,num,label in [(c1,'03','Easy questions'),(c2,'04','Medium questions'),(c3,'03','Hard questions')]:
        col.markdown(f'<div class="stat"><strong>{num}</strong><span>{label}</span></div>',unsafe_allow_html=True)
    st.write('')
    st.markdown('### Choose how answers are checked')
    st.radio('Feedback timing',['Check immediately','Check at the end'],key='mode',horizontal=True,
             help='Immediate checking shows correctness after each question. Full correct answers are revealed on the results page.')
    a,b=st.columns([2,1],vertical_alignment='bottom')
    with a:
        st.info('Each session has exactly 10 questions, ordered Easy → Medium → Hard. Tap a 3D model and drag to rotate it.')
    with b:
        if st.button('Start the quiz  →',type='primary',use_container_width=True):
            st.session_state.started=time.time();st.session_state.ended=None
            st.session_state.cursor=0;st.session_state.answers={};st.session_state.hint_counts={}
            for k in list(st.session_state.keys()):
                if k.startswith('choice_'): del st.session_state[k]
            st.session_state.screen='quiz';st.rerun()
    st.markdown('### What this platform demonstrates')
    st.markdown('''<div class="card"><strong>Section 1 · AI for Assessment</strong><p>Verified multiple-choice quiz, progressive hints, score, explanations and an answer key.</p>
    <strong>Section 2 · AI-Supported Feedback</strong><p>Three illustrative student answers, initial AI feedback drafts, teacher-reviewed revisions and recorded improvements.</p>
    <strong>Human review</strong><p>Quiz feedback is calculated by transparent rules; this demo does not call a live generative AI model.</p></div>''',unsafe_allow_html=True)

elif st.session_state.screen=='quiz':
    pos=st.session_state.cursor;q=QUESTIONS[pos]
    st.markdown(f"<div class='level'>{q['level']} · {q['topic']}</div>",unsafe_allow_html=True)
    a,b=st.columns([3,1])
    with a: st.subheader(f'Question {pos+1} of 10')
    with b: st.metric('Elapsed',elapsed())
    st.progress((pos+1)/10)
    left,right=st.columns([1,1.25],gap='large')
    with left:
        st.markdown(f"**Explore the {q['shape']}**")
        solid_plot(q['shape'])
        st.caption('Drag to rotate the model. Shape is illustrative; dimensions are given in the question.')
    with right:
        st.markdown(f'<div class="card"><h3 style="margin:.1rem 0 .2rem">{q["question"]}</h3><span class="smallnote">Choose one answer, or leave blank to skip.</span></div>',unsafe_allow_html=True)
        saved=st.session_state.answers.get(pos)
        # Each question uses its own stable input key; skip is explicit.
        chosen=st.radio('Answer',q['options'],index=q['options'].index(saved) if saved in q['options'] else None,
                        key=f'choice_{pos}',disabled=pos in st.session_state.answers,label_visibility='collapsed')
        hcount=st.session_state.hint_counts.get(pos,0)
        if hcount:
            for hint in q['hints'][:hcount]: st.info('💡 '+hint)
        if pos not in st.session_state.answers:
            ac,bc=st.columns(2)
            with ac:
                if st.button(f'Hint ({hcount}/2)',disabled=hcount>=2,use_container_width=True):
                    st.session_state.hint_counts[pos]=min(2,hcount+1);st.rerun()
            with bc:
                if st.button('Submit answer',type='primary',disabled=chosen is None,use_container_width=True):
                    st.session_state.answers[pos]=chosen;st.rerun()
            if st.button('Skip this question',use_container_width=True):go_to_next()
        else:
            if st.session_state.mode=='Check immediately':
                if saved==q['answer']:st.success('Correct! Well done. Your answer has been recorded.')
                else:st.warning('Not quite. Your answer has been recorded. Review the correct solution at the end.')
            else:st.info('Answer saved. You will see the correct answer in the results.')
            if st.button('See results →' if pos==9 else 'Next question →',type='primary',use_container_width=True):go_to_next()
    st.caption('All answers and full explanations become available after finishing the quiz.')

elif st.session_state.screen=='results':
    correct,incorrect,blank=result_summary()
    st.markdown('''<div class="hero"><div class="eyebrow">CHALLENGE COMPLETE</div>
    <h1>Your quiz results</h1><p>Use your mistakes as a guide for your next study session.</p></div>''',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric('Correct',f'{len(correct)}/10');b.metric('Incorrect',len(incorrect))
    c.metric('Unanswered',len(blank));d.metric('Time',elapsed())
    st.markdown('### Your personalized study feedback')
    for f in feedback_for_results():st.info(f)
    st.markdown('### Answer key and worked explanations')
    for idx,q in enumerate(QUESTIONS):
        chosen=st.session_state.answers.get(idx,'Not answered')
        state='✅' if idx in correct else ('⏭️' if idx in blank else '❌')
        with st.expander(f"{state} {idx+1}. {q['question']}"):
            st.write('**Your answer:**',chosen)
            st.write('**Correct answer:**',q['answer'])
            st.write('**Explanation:**',q['explanation'])
            if idx not in correct:st.write('**Study tip:**',q['wrong'])
    ca,cb=st.columns(2)
    with ca:
        if st.button('Try again',type='primary',use_container_width=True):restart();st.rerun()
    with cb:
        if st.button('View feedback samples',use_container_width=True):st.session_state.screen='samples';st.rerun()

elif st.session_state.screen=='samples':
    st.markdown('''<div class="hero"><div class="eyebrow">SECTION 2 · AI-SUPPORTED FEEDBACK</div>
    <h1>From AI draft to better feedback.</h1><p>Compare illustrative student responses, AI drafts and teacher-reviewed improvements.</p></div>''',unsafe_allow_html=True)
    st.markdown('### Sample question')
    st.info('A cube has a side length of 5 cm. Find its volume. **Answer key:** V = 5³ = 125 cm³.')
    for n,s in enumerate(SAMPLES,1):
        with st.expander(f'Student {n} · {s["title"]}',expanded=n==1):
            st.markdown('**Student answer**');st.write(s['answer'])
            st.markdown('**Initial AI-generated feedback (draft)**');st.warning(s['draft'])
            st.markdown('**Reviewed and improved feedback**');st.success(s['reviewed'])
            st.markdown('**What changed and why**');st.write(s['changed'])
    st.caption('The samples are fictional educational examples; the revised responses demonstrate teacher judgment rather than live AI grading.')
    st.markdown('### Why the feedback was improved')
    st.markdown('''<div class="card">The initial drafts used vague praise or generic corrections. The reviewed versions name the mathematical steps, identify misconceptions, explain the units and offer an actionable next step. The final decision remains with the teacher.</div>''',unsafe_allow_html=True)
    if st.button('See the AI prompts and reflection',type='primary'):
        st.session_state.screen='documentation';st.rerun()

elif st.session_state.screen=='documentation':
    st.markdown('''<div class="hero"><div class="eyebrow">PROJECT DOCUMENTATION</div>
    <h1>AI prompts & reflection.</h1><p>Make the AI contribution visible and keep your personal reflection your own.</p></div>''',unsafe_allow_html=True)
    st.markdown('### Prompts used in the project')
    for title,prompt in PROMPTS:
        with st.expander(title,expanded=True):st.code(prompt,language='text',wrap_lines=True)
    st.markdown('### Your personal reflection · 100–150 words')
    st.write('Write this part **in your own words**. Explain how AI helped, what it got wrong or did not do well, what you corrected, and what you would change next time.')
    reflection=st.text_area('My reflection',key='reflection',height=190,
                            placeholder='In this project, AI helped me ...\nHowever, I noticed ...\nI improved ...\nNext time, I would ...')
    words=len(reflection.split())
    st.caption(f'Word count: {words} / 100–150')
    if 100<=words<=150:st.success('Your reflection meets the word-count requirement.')
    elif reflection:st.warning('Adjust your reflection to 100–150 words before submitting.')
    st.info('Reflection is entered during this session and is not permanently saved by the website. Copy your final text into your assignment document.')
    st.markdown('### Project links')
    st.markdown('**Website:** https://geomaster-3d-lkfykpe296fwwawdk8akkf.streamlit.app')
    st.markdown('**GitHub:** https://github.com/kiyalbekdauren-hue/geomaster-3d')

st.markdown('---')
st.caption('GeoMaster 3D · AI-supported assessment demonstration · Quiz answers checked deterministically · Teacher-reviewed sample feedback')
