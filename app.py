import streamlit as st
import plotly.graph_objects as go
import random
import math

st.set_page_config(
    page_title="GeoMaster 3D",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp {
 font-family:Inter,sans-serif;
}
.stApp {
 background:
 radial-gradient(ellipse at 10% 5%,#1e3064 0%,transparent 40%),
 radial-gradient(ellipse at 90% 80%,#321b56 0%,transparent 40%),
 #090e20;
 color:#f5f7ff;
}
.block-container {max-width:1050px;padding-top:2rem}
h1,h2,h3,p {color:#f5f7ff}
.hero {
 text-align:center;
 padding:35px 10px;
}
.hero h1 {
 font-size:clamp(38px,6vw,64px);
 font-weight:800;
 background:linear-gradient(90deg,#65e5ff,#b48cff);
 -webkit-background-clip:text;
 -webkit-text-fill-color:transparent;
}
.hero p {color:#b8c7e6;font-size:17px}
.tag {
 display:inline-block;
 padding:8px 16px;
 border-radius:25px;
 background:#26366c;
 color:#91e3ff;
 font-size:12px;
 font-weight:800;
 letter-spacing:1px;
}
.panel {
 padding:22px;
 border:1px solid #34436d;
 border-radius:20px;
 background:rgba(25,34,70,.85);
 margin:10px 0;
}
.stButton>button {
 background:linear-gradient(100deg,#526bea,#9657e7);
 color:white!important;
 border:1px solid #8585ee;
 border-radius:13px;
 min-height:48px;
 font-weight:700;
 width:100%;
}
.stButton>button:hover {
 border-color:#8fe5ff;
 background:#364fc0;
}
div[data-testid="stRadio"] {
 background:#172141;
 border:1px solid #35456e;
 padding:15px;
 border-radius:15px;
}
div[data-testid="stAlert"] {border-radius:14px}
.score {
 font-size:72px;
 font-weight:800;
 color:#83e7ff;
 text-align:center;
}
.small {color:#a6b7d8}
</style>
""", unsafe_allow_html=True)

SHAPES = [
    "Cube", "Cuboid", "Sphere", "Cylinder",
    "Cone", "Square Pyramid", "Triangular Prism"
]

# ---------- 3D SHAPES ----------

def geometry(shape):
    if shape == "Cube":
        v = [
            (-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
            (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)
        ]
        f = [
            (0,1,2),(0,2,3),(4,6,5),(4,7,6),
            (0,4,5),(0,5,1),(1,5,6),(1,6,2),
            (2,6,7),(2,7,3),(3,7,4),(3,4,0)
        ]

    elif shape == "Cuboid":
        v = [
            (-1.5,-1,-.8),(1.5,-1,-.8),
            (1.5,1,-.8),(-1.5,1,-.8),
            (-1.5,-1,.8),(1.5,-1,.8),
            (1.5,1,.8),(-1.5,1,.8)
        ]
        f = [
            (0,1,2),(0,2,3),(4,6,5),(4,7,6),
            (0,4,5),(0,5,1),(1,5,6),(1,6,2),
            (2,6,7),(2,7,3),(3,7,4),(3,4,0)
        ]

    elif shape == "Square Pyramid":
        v = [
            (-1,-1,-1),(1,-1,-1),
            (1,1,-1),(-1,1,-1),(0,0,1.5)
        ]
        f = [
            (0,2,1),(0,3,2),
            (0,1,4),(1,2,4),(2,3,4),(3,0,4)
        ]

    elif shape == "Triangular Prism":
        v = [
            (-1,-1,-1),(1,-1,-1),(0,-1,1),
            (-1,1,-1),(1,1,-1),(0,1,1)
        ]
        f = [
            (0,2,1),(3,4,5),
            (0,1,4),(0,4,3),
            (1,2,5),(1,5,4),
            (2,0,3),(2,3,5)
        ]

    elif shape == "Sphere":
        v = []
        f = []
        n, m = 28, 18
        for a in range(m+1):
            theta = math.pi*a/m
            for b in range(n+1):
                phi = 2*math.pi*b/n
                v.append((
                    math.sin(theta)*math.cos(phi),
                    math.sin(theta)*math.sin(phi),
                    math.cos(theta)
                ))
        for a in range(m):
            for b in range(n):
                p = a*(n+1)+b
                f.extend([
                    (p,p+1,p+n+1),
                    (p+1,p+n+2,p+n+1)
                ])

    else:
        n = 48
        v = []
        f = []
        if shape == "Cone":
            for j in range(n):
                angle = 2*math.pi*j/n
                v.append((math.cos(angle),math.sin(angle),-1))
            v.append((0,0,1.5))
            v.append((0,0,-1))
            top = n
            bottom = n+1
            for j in range(n):
                k = (j+1)%n
                f.extend([(j,k,top),(bottom,k,j)])
        else:
            for z in [-1,1]:
                for j in range(n):
                    angle = 2*math.pi*j/n
                    v.append((math.cos(angle),math.sin(angle),z))
            v.extend([(0,0,-1),(0,0,1)])
            for j in range(n):
                k = (j+1)%n
                f.extend([
                    (j,k,n+k),(j,n+k,n+j),
                    (2*n,k,j),(2*n+1,n+j,n+k)
                ])

    return v, f


def show_shape(shape):
    vertices, faces = geometry(shape)
    x,y,z = zip(*vertices)
    i,j,k = zip(*faces)

    fig = go.Figure()

    fig.add_trace(go.Mesh3d(
        x=x,y=y,z=z,
        i=i,j=j,k=k,
        color="#788cff",
        opacity=.87,
        flatshading=True,
        lighting=dict(
            ambient=.65,
            diffuse=.8,
            specular=.5,
            roughness=.35
        ),
        hoverinfo="skip"
    ))

    # Draw edges for polyhedra
    if shape in ["Cube","Cuboid","Square Pyramid","Triangular Prism"]:
        edge_set = set()
        for face in faces:
            for a,b in [
                (face[0],face[1]),
                (face[1],face[2]),
                (face[2],face[0])
            ]:
                edge_set.add(tuple(sorted((a,b))))

        ex,ey,ez = [],[],[]
        for a,b in edge_set:
            for index in [a,b]:
                ex.append(vertices[index][0])
                ey.append(vertices[index][1])
                ez.append(vertices[index][2])
            ex.append(None)
            ey.append(None)
            ez.append(None)

        fig.add_trace(go.Scatter3d(
            x=ex,y=ey,z=ez,
            mode="lines",
            line=dict(color="#c5f2ff",width=4),
            hoverinfo="skip"
        ))

    fig.update_layout(
        height=340,
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.7,y=1.5,z=1.2))
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar":False,"scrollZoom":True}
    )
    st.caption("👆 Drag to rotate • Pinch to zoom")


# ---------- QUESTION GENERATOR ----------

def question(shape, level):
    a = random.randint(2,18)
    b = random.randint(2,16)
    c = random.randint(2,14)
    pi = 3.14

    # Each question has:
    # question text, correct answer, hint, explanation

    if level == "Easy":
        if shape == "Cube":
            tasks = [
                ("How many faces does a cube have?",6,
                 "Count its square surfaces.","A cube has 6 faces."),
                ("How many edges does a cube have?",12,
                 "Count where two faces meet.","A cube has 12 edges."),
                ("How many vertices does a cube have?",8,
                 "Count the corners.","A cube has 8 vertices."),
                (f"A cube has side {a} cm. Find its volume.",a**3,
                 "Use V = a³.",f"V = {a}³ = {a**3} cm³.")
            ]

        elif shape == "Cuboid":
            tasks = [
                ("How many faces does a cuboid have?",6,
                 "Think of a box.","A cuboid has 6 faces."),
                ("How many edges does a cuboid have?",12,
                 "Count the straight edges.","A cuboid has 12 edges."),
                (f"A cuboid measures {a} × {b} × {c} cm. Find its volume.",
                 a*b*c,"Multiply length, width and height.",
                 f"V = {a} × {b} × {c} = {a*b*c} cm³.")
            ]

        elif shape == "Sphere":
            tasks = [
                ("How many vertices does a sphere have?",0,
                 "Does a sphere have corners?","A sphere has 0 vertices."),
                (f"A sphere has radius {a} cm. Find its diameter.",
                 2*a,"Diameter = 2 × radius.",
                 f"d = 2 × {a} = {2*a} cm."),
                (f"A sphere has diameter {2*a} cm. Find its radius.",
                 a,"Radius = diameter ÷ 2.",
                 f"r = {2*a} ÷ 2 = {a} cm.")
            ]

        elif shape == "Cylinder":
            tasks = [
                ("How many flat circular faces does a cylinder have?",2,
                 "Look at the top and bottom.",
                 "A cylinder has two flat circular faces."),
                (f"A cylinder has radius {a} cm. Find its diameter.",
                 2*a,"Double the radius.",f"d = {2*a} cm."),
                (f"Find the volume of a cylinder with radius {a} cm and height {b} cm. Use π = 3.14.",
                 round(pi*a*a*b,2),"Use V = πr²h.",
                 f"V = 3.14 × {a}² × {b} = {round(pi*a*a*b,2)} cm³.")
            ]

        elif shape == "Cone":
            tasks = [
                ("How many vertices does a cone have?",1,
                 "Look at its pointed tip.","A cone has one vertex."),
                ("How many flat circular bases does a cone have?",1,
                 "Look at the bottom.","A cone has one circular base."),
                (f"A cone has radius {a} cm and height {b} cm. Find its volume using π = 3.14.",
                 round(pi*a*a*b/3,2),"Use V = πr²h/3.",
                 f"V = {round(pi*a*a*b/3,2)} cm³.")
            ]

        elif shape == "Square Pyramid":
            tasks = [
                ("How many faces does a square pyramid have?",5,
                 "Count four triangles and the base.",
                 "There are 4 triangles and 1 square."),
                ("How many vertices does a square pyramid have?",5,
                 "Count the base corners and apex.",
                 "There are 4 base vertices and 1 apex."),
                (f"A square pyramid has base side {a} cm and height {b} cm. Find its volume.",
                 round(a*a*b/3,2),"Use V = a²h/3.",
                 f"V = {round(a*a*b/3,2)} cm³.")
            ]

        else:
            tasks = [
                ("How many faces does a triangular prism have?",5,
                 "Count the two triangles and three rectangles.",
                 "A triangular prism has 5 faces."),
                ("How many vertices does a triangular prism have?",6,
                 "Each triangular end has 3 vertices.",
                 "There are 6 vertices."),
                (f"A triangular prism has triangle base {a} cm, triangle height {b} cm and length {c} cm. Find its volume.",
                 round(a*b*c/2,2),
                 "Use V = ½ × base × triangle height × length.",
                 f"V = {round(a*b*c/2,2)} cm³.")
            ]

    elif level == "Medium":
        if shape == "Cube":
            tasks = [
                (f"Find the surface area of a cube with side {a} cm.",
                 6*a*a,"Use SA = 6a².",
                 f"SA = 6 × {a}² = {6*a*a} cm²."),
                (f"A cube has volume {a**3} cm³. Find its side.",
                 a,"Take the cube root.",
                 f"Cube root of {a**3} = {a} cm."),
                (f"Find the space diagonal of a cube with side {a} cm. Round to 2 decimals.",
                 round(a*math.sqrt(3),2),"Use d = a√3.",
                 f"d = {a}√3 ≈ {round(a*math.sqrt(3),2)} cm.")
            ]

        elif shape == "Cuboid":
            sa = 2*(a*b+a*c+b*c)
            tasks = [
                (f"Find the surface area of a cuboid measuring {a} × {b} × {c} cm.",
                 sa,"Use SA = 2(lw+lh+wh).",
                 f"SA = {sa} cm²."),
                (f"A cuboid has volume {a*b*c} cm³, length {a} cm and width {b} cm. Find its height.",
                 c,"Use h = V/(lw).",f"h = {c} cm."),
                (f"Find the space diagonal of a cuboid measuring {a} × {b} × {c} cm. Round to 2 decimals.",
                 round(math.sqrt(a*a+b*b+c*c),2),
                 "Use d = √(l²+w²+h²).",
                 f"d = {round(math.sqrt(a*a+b*b+c*c),2)} cm.")
            ]

        elif shape == "Sphere":
            tasks = [
                (f"Find the surface area of a sphere with radius {a} cm. Use π = 3.14.",
                 round(4*pi*a*a,2),"Use SA = 4πr².",
                 f"SA = {round(4*pi*a*a,2)} cm²."),
                (f"Find the volume of a sphere with radius {a} cm. Use π = 3.14.",
                 round(4*pi*a**3/3,2),"Use V = 4πr³/3.",
                 f"V = {round(4*pi*a**3/3,2)} cm³.")
            ]

        elif shape == "Cylinder":
            tasks = [
                (f"Find the curved surface area of a cylinder with radius {a} cm and height {b} cm. Use π = 3.14.",
                 round(2*pi*a*b,2),"Use CSA = 2πrh.",
                 f"CSA = {round(2*pi*a*b,2)} cm²."),
                (f"Find the total surface area of a closed cylinder with radius {a} cm and height {b} cm. Use π = 3.14.",
                 round(2*pi*a*(a+b),2),"Use SA = 2πr(r+h).",
                 f"SA = {round(2*pi*a*(a+b),2)} cm².")
            ]

        elif shape == "Cone":
            slant = math.sqrt(a*a+b*b)
            tasks = [
                (f"A cone has radius {a} cm and height {b} cm. Find its slant height to 2 decimals.",
                 round(slant,2),"Use l = √(r²+h²).",
                 f"l = {round(slant,2)} cm."),
                (f"Find the total surface area of a cone with radius {a} cm and height {b} cm. Use π = 3.14 and round to 2 decimals.",
                 round(pi*a*(a+slant),2),
                 "First find slant height, then use SA = πr(r+l).",
                 f"SA = {round(pi*a*(a+slant),2)} cm².")
            ]

        elif shape == "Square Pyramid":
            slant = math.sqrt(b*b+(a/2)**2)
            tasks = [
                (f"A square pyramid has base side {a} cm and height {b} cm. Find its slant height to 2 decimals.",
                 round(slant,2),"Use l = √(h²+(a/2)²).",
                 f"l = {round(slant,2)} cm."),
                (f"Find the volume of a square pyramid with base side {a} cm and height {b} cm.",
                 round(a*a*b/3,2),"Use V = a²h/3.",
                 f"V = {round(a*a*b/3,2)} cm³.")
            ]

        else:
            tasks = [
                (f"Find the volume of a triangular prism with triangle base {a} cm, triangle height {b} cm and prism length {c} cm.",
                 round(a*b*c/2,2),"Use V = ½bhl.",
                 f"V = {round(a*b*c/2,2)} cm³."),
                (f"A triangular prism has volume {a*b*c/2:.2f} cm³. Its triangle has base {a} cm and height {b} cm. Find the prism length.",
                 c,"Divide volume by triangular area.",
                 f"Length = {c} cm.")
            ]

    else:
        scale = random.choice([2,3,4])

        if shape == "Cube":
            tasks = [
                (f"A cube's side increases by a factor of {scale}. By what factor does its volume increase?",
                 scale**3,"Volume scales with the cube of the factor.",
                 f"Factor = {scale}³ = {scale**3}."),
                (f"A cube has surface area {6*a*a} cm². Find its volume.",
                 a**3,"Find its side using SA = 6a².",
                 f"Side = {a}; volume = {a**3} cm³.")
            ]

        elif shape == "Cuboid":
            tasks = [
                (f"All dimensions of a cuboid are multiplied by {scale}. By what factor does its surface area increase?",
                 scale**2,"Area scales by the square of the factor.",
                 f"Factor = {scale}² = {scale**2}."),
                (f"A cuboid has volume {a*b*c} cm³, width {b} cm and height {c} cm. Find its length.",
                 a,"Use l = V/(wh).",
                 f"Length = {a} cm.")
            ]

        elif shape == "Sphere":
            tasks = [
                (f"The radius of a sphere is multiplied by {scale}. By what factor does its volume increase?",
                 scale**3,"Volume is proportional to r³.",
                 f"Factor = {scale**3}."),
                (f"A sphere has diameter {2*a} cm. Find its volume using π = 3.14.",
                 round(4*pi*a**3/3,2),
                 "First divide the diameter by two.",
                 f"Radius = {a}; volume = {round(4*pi*a**3/3,2)} cm³.")
            ]

        elif shape == "Cylinder":
            tasks = [
                (f"A cylinder's radius is multiplied by {scale} while its height stays the same. By what factor does its volume increase?",
                 scale**2,"Volume is proportional to r².",
                 f"Factor = {scale}² = {scale**2}."),
                (f"A cylinder has volume {round(pi*a*a*b,2)} cm³ and radius {a} cm. Find its height using π = 3.14.",
                 b,"Use h = V/(πr²).",
                 f"Height = {b} cm.")
            ]

        elif shape == "Cone":
            tasks = [
                (f"Every dimension of a cone is multiplied by {scale}. By what factor does its volume increase?",
                 scale**3,"Volume scales cubically.",
                 f"Factor = {scale**3}."),
                (f"A cone has radius {a} cm and height {b} cm. Find its slant height to 2 decimals.",
                 round(math.sqrt(a*a+b*b),2),
                 "Use the Pythagorean theorem.",
                 f"Slant height = {round(math.sqrt(a*a+b*b),2)} cm.")
            ]

        elif shape == "Square Pyramid":
            tasks = [
                (f"Every dimension of a square pyramid is multiplied by {scale}. By what factor does its volume increase?",
                 scale**3,"Volume scales cubically.",
                 f"Factor = {scale**3}."),
                (f"A square pyramid has volume {a*a*b/3:.2f} cm³ and base side {a} cm. Find its height to 2 decimals.",
                 round(3*(a*a*b/3)/(a*a),2),
                 "Use h = 3V/a².",
                 f"Height = {b} cm.")
            ]

        else:
            tasks = [
                (f"All dimensions of a triangular prism are multiplied by {scale}. By what factor does its volume increase?",
                 scale**3,"Volume scales cubically.",
                 f"Factor = {scale**3}."),
                (f"A triangular prism has volume {a*b*c/2:.2f} cm³. Its triangular base has base {a} cm and height {b} cm. Find the prism length.",
                 c,"Divide the volume by triangular area.",
                 f"Length = {c} cm.")
            ]

    return random.choice(tasks)


def options_for(answer):
    result = [answer]
    attempts = 0

    while len(result) < 4 and attempts < 100:
        attempts += 1

        if isinstance(answer,int):
            difference = random.randint(1,max(4,int(abs(answer)*.35)+2))
            candidate = max(0,answer+random.choice([-1,1])*difference)
        else:
            candidate = round(
                max(0,answer*random.choice([.5,.75,1.25,1.5,2])),
                2
            )

        if candidate not in result:
            result.append(candidate)

    random.shuffle(result)
    return result


def start_game(level):
    questions = []
    used = set()
    attempts = 0

    while len(questions) < 10 and attempts < 1000:
        attempts += 1
        shape = random.choice(SHAPES)
        text,answer,hint,explanation = question(shape,level)

        if text in used:
            continue

        used.add(text)
        questions.append({
            "shape":shape,
            "text":text,
            "answer":answer,
            "hint":hint,
            "explanation":explanation,
            "options":options_for(answer)
        })

    st.session_state.level = level
    st.session_state.questions = questions
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.checked = False
    st.session_state.hint_visible = False
    st.session_state.history = []
    st.session_state.run_id += 1
    st.session_state.page = "quiz"


# ---------- SESSION STATE ----------

defaults = {
    "page":"home",
    "level":"Easy",
    "questions":[],
    "index":0,
    "score":0,
    "checked":False,
    "hint_visible":False,
    "history":[],
    "run_id":0
}

for key,value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- HEADER ----------

st.markdown(
    '<h3 style="color:#91e6ff;">◈ GeoMaster 3D</h3>',
    unsafe_allow_html=True
)
st.divider()


# ---------- WELCOME PAGE ----------

if st.session_state.page == "home":

    st.markdown("""
    <div class="hero">
      <span class="tag">INTERACTIVE MATHEMATICS</span>
      <h1>Welcome to GeoMaster 3D</h1>
      <p>Explore 3D shapes. Challenge your mind.<br>
      Become a geometry master.</p>
    </div>
    """,unsafe_allow_html=True)

    show_shape("Cube")

    st.markdown("## Choose Your Difficulty")
    st.caption("10 random questions in every challenge.")

    levels = [
        ("Easy","🌱","Basic shapes, faces, edges and volume"),
        ("Medium","⚡","Surface area, diagonals and formulas"),
        ("Hard","🚀","Advanced geometry and scaling")
    ]

    cols = st.columns(3)

    for col,(level,emoji,description) in zip(cols,levels):
        with col:
            st.markdown(f"""
            <div class="panel">
              <h1>{emoji}</h1>
              <h2>{level}</h2>
              <p class="small">{description}</p>
            </div>
            """,unsafe_allow_html=True)

            if st.button(
                f"Start {level}",
                key=f"start_{level}"
            ):
                start_game(level)
                st.rerun()

    st.markdown("---")
    st.caption("7 Shapes • 3 Levels • Unlimited Practice")


# ---------- QUIZ PAGE ----------

elif st.session_state.page == "quiz":

    index = st.session_state.index
    q = st.session_state.questions[index]

    c1,c2 = st.columns([3,1])

    with c1:
        st.subheader(f"{st.session_state.level} Challenge")
        st.write(f"Question {index+1} of 10")

    with c2:
        st.metric("Score",f"{st.session_state.score}/10")

    st.progress((index+1)/10)

    left,right = st.columns([1,1.15])

    with left:
        st.markdown(f"### {q['shape']}")
        show_shape(q["shape"])

    with right:
        st.markdown(
            '<span class="tag">GEOMETRY CHALLENGE</span>',
            unsafe_allow_html=True
        )
        st.markdown(f"### {q['text']}")

        if not st.session_state.checked:

            selected = st.radio(
                "Choose the correct answer:",
                q["options"],
                index=None,
                key=f"choice_{st.session_state.run_id}_{index}"
            )

            a,b = st.columns(2)

            with a:
                if st.button("💡 Get Hint"):
                    st.session_state.hint_visible = True

            with b:
                if st.button(
                    "Check Answer",
                    disabled=selected is None
                ):
                    correct = math.isclose(
                        float(selected),
                        float(q["answer"]),
                        rel_tol=1e-9,
                        abs_tol=1e-9
                    )

                    if correct:
                        st.session_state.score += 1

                    st.session_state.history.append({
                        "question":q["text"],
                        "selected":selected,
                        "answer":q["answer"],
                        "correct":correct,
                        "explanation":q["explanation"]
                    })


                    st.session_state.checked = True
                    st.rerun()

            if st.session_state.hint_visible:
                st.info("💡 Hint: "+q["hint"])

        else:
            result = st.session_state.history[-1]

            if result["correct"]:
                st.success("🎉 Correct! Excellent work!")
            else:
                st.error(
                    f"Not quite! Correct answer: {q['answer']}"
                )

            st.info(
                "📘 Explanation: "+q["explanation"]
            )

            if index < 9:
                if st.button("Next Question →"):
                    st.session_state.index += 1
                    st.session_state.checked = False
                    st.session_state.hint_visible = False
                    st.rerun()
            else:
                if st.button("View Results 🏆"):
                    st.session_state.page = "results"
                    st.rerun()

    st.divider()

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ---------- RESULTS PAGE ----------

elif st.session_state.page == "results":

    score = st.session_state.score

    if score == 10:
        title = "Perfect Score! 🏆"
        message = "You are a true geometry master!"
    elif score >= 8:
        title = "Amazing Work! 🌟"
        message = "Excellent understanding of 3D geometry!"
    elif score >= 5:
        title = "Great Progress! 🚀"
        message = "Keep practicing and improving!"
    else:
        title = "Keep Learning! 💪"
        message = "Every attempt helps you grow!"

    st.markdown(
        f'<div class="hero"><span class="tag">CHALLENGE COMPLETE</span>'
        f'<h1>{title}</h1><div class="score">{score}/10</div>'
        f'<h2>{score*10}% Accuracy</h2>'
        f'<p>{message}</p></div>',
        unsafe_allow_html=True
    )

    c1,c2,c3 = st.columns(3)
    c1.metric("Correct",score)
    c2.metric("Incorrect",10-score)
    c3.metric("Level",st.session_state.level)

    st.markdown("## 📖 Answer Review")

    for i,item in enumerate(st.session_state.history):
        symbol = "✅" if item["correct"] else "❌"

        with st.expander(
            f"{symbol} Question {i+1}: {item['question']}"
        ):
            st.write("Your answer:",item["selected"])
            st.write("Correct answer:",item["answer"])
            st.info(item["explanation"])

    a,b = st.columns(2)

    with a:
        if st.button("🔄 Play Again"):
            start_game(st.session_state.level)
            st.rerun()

    with b:
        if st.button("🏠 Choose Another Level"):
            st.session_state.page = "home"
            st.rerun()

st.markdown("---")
st.caption("GeoMaster 3D | Learn • Explore • Achieve")
