import streamlit as st
import requests
import random
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from googletrans import Translator
import time
import base64

# -----------------------------
# 1. 배경 이미지 세팅 (반투명 처리)
# -----------------------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        .card {{
            background: rgba(255,255,255,0.85);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .cols img {{
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("12b0edc7-0e10-4ecd-8ce3-95bd6f047eb9.png")

# -----------------------------
# 2. 타입 및 번역기
# -----------------------------
TYPE_LIST = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting',
             'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost',
             'dragon', 'dark', 'steel', 'fairy']

translator = Translator()

def translate_text(text, dest='ko'):
    try:
        return translator.translate(text, dest=dest).text
    except:
        return text

# -----------------------------
# 3. 유틸 함수
# -----------------------------
def types_to_vector(types):
    vec = np.zeros(len(TYPE_LIST))
    for t in types:
        if t in TYPE_LIST:
            vec[TYPE_LIST.index(t)] = 1
    return vec

def get_evolution_stage(name, evolutions):
    try:
        return evolutions.index(name) + 1
    except:
        return 1

@st.cache_data(show_spinner=False)
def load_pokemon_data(max_id=1025):  
    pokemon_data = {}
    progress = st.progress(0)
    status_text = st.empty()

    for idx, poke_id in enumerate(range(1, max_id + 1), 1):
        try:
            p = requests.get(f"https://pokeapi.co/api/v2/pokemon/{poke_id}/", timeout=5).json()
            species = requests.get(p['species']['url'], timeout=5).json()

            name_ko = next((e['name'] for e in species['names'] if e['language']['name']=='ko'), None)
            if not name_ko:
                name_ko = translate_text(species['name'])

            types = [t['type']['name'] for t in p['types']]

            evo_chain = requests.get(species['evolution_chain']['url'], timeout=5).json()
            evolutions = []
            def parse(chain):
                evolutions.append(chain['species']['name'])
                for e in chain.get('evolves_to', []):
                    parse(e)
            parse(evo_chain['chain'])

            ko_texts = [f['flavor_text'] for f in species['flavor_text_entries'] if f['language']['name']=='ko']
            if ko_texts:
                description = ko_texts[0].replace('\n',' ').replace('\x0c',' ')
            else:
                en_texts = [f['flavor_text'] for f in species['flavor_text_entries'] if f['language']['name']=='en']
                description = translate_text(en_texts[0]).replace('\n',' ').replace('\x0c',' ') if en_texts else ''

            height = p.get('height', 0) / 10
            weight = p.get('weight', 0) / 10

            image_url = p['sprites']['other']['official-artwork']['front_default']

            pokemon_data[name_ko] = {
                'types': types,
                'evolutions': evolutions,
                'description': description,
                'height': height,
                'weight': weight,
                'image_url': image_url
            }

            status_text.text(f"불러오는 중... {idx}/{max_id}")
            progress.progress(idx / max_id)
            time.sleep(0.01)

        except:
            continue

    progress.progress(1.0)
    status_text.text("데이터 로딩 완료!")
    return pokemon_data

def get_pokemon_vector(name, info, model):
    type_vec = types_to_vector(info['types'])
    evo_stage = get_evolution_stage(name, info['evolutions'])
    evo_vec = np.array([evo_stage])
    tokens = info['description'].split()
    desc_vecs = [model.wv[t] for t in tokens if t in model.wv]
    desc_vec = np.mean(desc_vecs, axis=0) if desc_vecs else np.zeros(model.vector_size)
    phys_vec = np.array([info['height'] / 10, info['weight'] / 100])
    return np.concatenate([type_vec, evo_vec, desc_vec, phys_vec])

def generate_question(pokemon_data, model):
    names = list(pokemon_data.keys())
    # ABC가 서로 유사도가 높은 3마리로 묶기
    sample_names = random.sample(names, 20)
    sample_vecs = [get_pokemon_vector(n, pokemon_data[n], model) for n in sample_names]
    sim_matrix = cosine_similarity(sample_vecs)
    # 가장 유사도가 높은 3마리 조합 찾기
    best_score = -1
    best_triplet = None
    for i in range(len(sample_names)):
        for j in range(i+1, len(sample_names)):
            for k in range(j+1, len(sample_names)):
                score = sim_matrix[i][j] + sim_matrix[i][k] + sim_matrix[j][k]
                if score > best_score:
                    best_score = score
                    best_triplet = (sample_names[i], sample_names[j], sample_names[k])
    A, B, C = best_triplet
    # D는 ABC와 유사도가 가장 높은 나머지 한 마리
    abc_vec = np.mean([get_pokemon_vector(n, pokemon_data[n], model) for n in (A, B, C)], axis=0)
    rest_names = [n for n in names if n not in best_triplet]
    rest_vecs = [get_pokemon_vector(n, pokemon_data[n], model) for n in rest_names]
    sims = cosine_similarity([abc_vec], rest_vecs)[0]
    D = rest_names[np.argmax(sims)]

    AB = cosine_similarity([get_pokemon_vector(A, pokemon_data[A], model)],
                           [get_pokemon_vector(B, pokemon_data[B], model)])[0][0]
    AC = cosine_similarity([get_pokemon_vector(A, pokemon_data[A], model)],
                           [get_pokemon_vector(C, pokemon_data[C], model)])[0][0]
    BC = cosine_similarity([get_pokemon_vector(B, pokemon_data[B], model)],
                           [get_pokemon_vector(C, pokemon_data[C], model)])[0][0]

    relations = {f"{A}-{B}": AB, f"{A}-{C}": AC, f"{B}-{C}": BC}
    return A, B, C, D, best_score, relations

# -----------------------------
# 4. Streamlit 메인
# -----------------------------
st.title("⚡ 포켓몬 관계성 게임 ⚡")

if 'pokemon_data' not in st.session_state:
    with st.spinner("데이터 불러오는 중..."):
        st.session_state['pokemon_data'] = load_pokemon_data()
pokemon_data = st.session_state['pokemon_data']

st.info("임베딩 학습 중...")
corpus = [[*name.split(), *info['types'], *info['description'].split()]
          for name, info in pokemon_data.items()]
model = Word2Vec(corpus, vector_size=50, window=5, min_count=1, workers=2, seed=42)

if 'current_question' not in st.session_state or st.session_state.get('next_question', False):
    st.session_state['current_question'] = generate_question(pokemon_data, model)
    st.session_state['show_answer'] = False
    st.session_state['user_input'] = ""
    st.session_state['next_question'] = False

A, B, C, D, score, relations = st.session_state['current_question']

# -----------------------------
# 문제 표시
# -----------------------------
st.markdown("<div class='card'><h4>문제 포켓몬 3마리 (A : B, C : ?)</h4></div>", unsafe_allow_html=True)
cols = st.columns(3)
for col, name in zip(cols, (A, B, C)):
    col.image(pokemon_data[name]['image_url'], caption=name, width=400)

# -----------------------------
# 정답 입력 및 처리
# -----------------------------
user_input = st.text_input("정답 포켓몬 이름을 입력하세요", value=st.session_state.get('user_input', ""))

if user_input:
    st.session_state['user_input'] = user_input
    answer_name = user_input.strip()
    if answer_name in pokemon_data:
        st.markdown("<div class='card'><h4>입력한 포켓몬</h4></div>", unsafe_allow_html=True)
        st.image(pokemon_data[answer_name]['image_url'], caption=answer_name, width=400)

        st.markdown("<div class='card'><h4>입력한 포켓몬과 문제 3마리 관계성</h4></div>", unsafe_allow_html=True)
        relation_data = []
        for name in [A, B, C]:
            sim_val = cosine_similarity(
                [get_pokemon_vector(name, pokemon_data[name], model)],
                [get_pokemon_vector(answer_name, pokemon_data[answer_name], model)]
            )[0][0]
            relation_data.append((name, f"{sim_val*100:.2f}%"))
        st.table(relation_data)

        # 100% 일치(관계도 100%)면 바로 정답 처리
        if answer_name == D or any(float(val[:-1]) == 100.0 for _, val in relation_data):
            st.session_state['show_answer'] = True
        if st.session_state['show_answer']:
            st.success(f"정답! {D}와 문제 3마리와의 관계성:")
            st.markdown("<div class='card'><h4>정답 포켓몬</h4></div>", unsafe_allow_html=True)
            st.image(pokemon_data[D]['image_url'], caption=D, width=400)

            st.markdown("<div class='card'><h4>3마리와 정답 포켓몬 관계성</h4></div>", unsafe_allow_html=True)
            relation_data = []
            for name in [A, B, C]:
                sim_val = cosine_similarity(
                    [get_pokemon_vector(name, pokemon_data[name], model)],
                    [get_pokemon_vector(D, pokemon_data[D], model)]
                )[0][0]
                relation_data.append((name, f"{sim_val*100:.2f}%"))
            st.table(relation_data)

            st.markdown("<div class='card'><h4>문제 3마리 내부 관계성</h4></div>", unsafe_allow_html=True)
            relation_table = [(k, f"{v*100:.2f}%") for k, v in relations.items()]
            st.table(relation_table)

            col1, col2 = st.columns(2)
            if col1.button("다음 문제로 넘어가기"):
                st.session_state['next_question'] = True
                st.session_state['user_input'] = ""
                st.session_state['show_answer'] = False
                st.rerun()
            if col2.button("같은 문제 다시 풀기"):
                st.session_state['show_answer'] = False
                st.session_state['user_input'] = ""
                st.rerun()
        else:
            col1, col2 = st.columns(2)
            if col1.button("다음 문제로 넘어가기"):
                st.session_state['next_question'] = True
                st.session_state['user_input'] = ""
                st.session_state['show_answer'] = False
                st.rerun()
            if col2.button("같은 문제 다시 풀기"):
                st.session_state['show_answer'] = False
                st.session_state['user_input'] = ""
                st.rerun()
    else:
        st.error("입력한 포켓몬 이름이 데이터에 없습니다. 다시 입력해주세요.")