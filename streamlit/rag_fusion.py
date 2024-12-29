import streamlit as st
import sys
import os
sys.path.append('..')
from chains.fusion_gpt_with_filter import combine_chain
from dotenv import load_dotenv
from streamlit_pdf_viewer import pdf_viewer
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import base64

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
SMP_KEYS = os.getenv('SMP_KEYS')
SOP_KEYS = os.getenv('SOP_KEYS')
K_VALUES = int(os.getenv('K_VALUES'))

def contains_any_phrase(string, phrase_list):
    # 將清單中的詞組使用逗號分隔轉為列表
    phrases = phrase_list.split(',')
    
    # 檢查是否有任一詞組存在於字串中
    for phrase in phrases:
        if phrase in string:
            return True
    return False

def filtered_retiever(question):
    if contains_any_phrase(question,SMP_KEYS):
        db_path = "./db/only_table"
    elif contains_any_phrase(question,SOP_KEYS):
        db_path = "./db/only_image"
    else:
        db_path = "./db/combine"
    db = FAISS.load_local(
        folder_path=db_path, 
        embeddings=OpenAIEmbeddings(),
        allow_dangerous_deserialization=True)
    retriever=db.as_retriever(search_kwargs={"k": K_VALUES,"fetch_k":K_VALUES*2})
    res = retriever.invoke(question)
    
    return res


st.title('上水ＧＰＴ')
# Initialize session state for button visibility
if 'button_one_clicked' not in st.session_state:
    st.session_state['button_one_clicked'] = False
if 'sop_m' not in st.session_state:
    st.session_state['sop_m'] = ""
if 'button_two_clicked' not in st.session_state:
    st.session_state['button_two_clicked'] = False
if 'smp_m' not in st.session_state:
    st.session_state['smp_m'] = ""
if 'text_content' not in st.session_state:
    st.session_state['text_content'] = ""
    
# Add two buttons with mutual control
st.text("常見問題：")
if st.button('設備異常'):
    st.session_state['button_one_clicked'] = not st.session_state['button_one_clicked']
    st.session_state['button_two_clicked'] = False
    st.session_state['text_content'] = f"請問設備『{st.session_state['smp_m']}』的操作流程"
if st.button('操作流程'):
    st.session_state['button_two_clicked'] = not st.session_state['button_two_clicked']
    st.session_state['button_one_clicked'] = False
    st.session_state['text_content'] = f"設備『{st.session_state['sop_m']}』發生故障，請問該如何排除"

if st.session_state['button_two_clicked']:
    smp_options = ["電動進流閘門", "攔污柵", "曝氣沉砂池洗砂機","二級沉澱池","砂濾設備","回收水自動加壓系統","紫外線消毒設備","帶濾式脫水機","污泥乾燥系統"]
    selected_smp = st.selectbox("請選擇設備：", smp_options)
    st.session_state['smp_m'] = selected_smp
    st.session_state['text_content'] = f"請問設備『{st.session_state['smp_m']}』的操作流程"
if st.session_state['button_one_clicked']:
    sop_options = ["閘門類", "沉水式抽水泵", "沉水式攪拌機","電動攔污柵","洗砂機","空氣壓縮機","乾井式豎軸離心泵","刮泥機","魯式鼓風機","泡藥設備","污泥脫水機","電動吊車","螺旋泵"]
    selected_sop = st.selectbox("請選擇設備：", sop_options)
    st.session_state['sop_m'] = selected_sop
    st.session_state['text_content'] = f"設備『{st.session_state['sop_m']}』發生故障，請問該如何排除"
with st.form('my_form'):
    text = st.text_area('Enter text:', st.session_state['text_content'])
    submitted = st.form_submit_button('Submit')
    if submitted:
        if len(text.strip())>0:
            docs = {}
            img_list = []
            st.write_stream(combine_chain.stream(text))
            resources = filtered_retiever(text)
            if len(resources)>0:
                with st.popover("Open Resources",use_container_width=True):
                    display_list={'標準維護程序書.pdf':[],'標準操作程序書.pdf':[]}
                    for idx, doc in enumerate(resources):
                        metadata = doc.metadata
                        if idx>0:
                            st.divider()
                            
                        if metadata['type']=="image":
                            st.subheader('來源圖片：')
                            st.image(base64.b64decode(metadata['original_content']))
                    
                        else:
                            if metadata.get('page') not in display_list[metadata.get('file')]:
                                st.subheader(f"""來源：『{metadata.get('file')}』 """, divider=True)
                                pdf_viewer(
                                f"""./pdf/{metadata.get('file')}""",
                                width=700,
                                height=800,
                                pages_to_render=[metadata.get('page')],
                                )
                                display_list[metadata.get('file')].append(metadata.get('page'))
                        
        else:
            st.write("""請提供具體的問題或設備名稱，以便我能夠針對您的需求進行操作方式或故障排除的解答。  謝謝""")
