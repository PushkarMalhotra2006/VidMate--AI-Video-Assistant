import warnings
warnings.filterwarnings('ignore')

import streamlit as st
from datetime import datetime
from main import transcript_pipeline, pipeline
from core.rag_engine import ask_question

# Page config
st.set_page_config(
    page_title="VidMate",
    page_icon="🎞️",
    layout="wide"
)

# Subtle, polished styling
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f7 100%);
    }
    
    .hero-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    
    .hero-title {
        font-size: 1.6em;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 6px 0;
    }
    
    .hero-subtitle {
        font-size: 0.95em;
        color: #64748b;
        margin: 0;
    }

    .input-heading {
        font-size: 1.15em;
        font-weight: 450;
        color: #1e293b;
        margin-bottom: 14px;
    }
    
    .input-label {
        font-size: 0.95em;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 10px;
        display: block;
    }
    
    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
    }
    
    .feature-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon {
        font-size: 1.8em;
        margin-bottom: 8px;
    }
    
    .feature-title {
        font-size: 1.05em;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 6px 0;
    }
    
    .feature-desc {
        font-size: 0.85em;
        color: #64748b;
        margin: 0 0 12px 0;
        line-height: 1.4;
    }
    
    .section-spacing {
        margin: 24px 0;
    }
    
    .results-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_transcript' not in st.session_state:
    st.session_state.current_transcript = None
if 'summary_result' not in st.session_state:
    st.session_state.summary_result = None
if 'notes_result' not in st.session_state:
    st.session_state.notes_result = None
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_choice' not in st.session_state:
    st.session_state.selected_choice = None
if 'last_source' not in st.session_state:
    st.session_state.last_source = None

# Hero card
st.markdown("""
<div class="hero-card">
    <h1 class="hero-title">🎞️ VidMate</h1>
    <p class="hero-subtitle">AI Video Assistant to generate summary, notes or ask doubts from Youtube Videos or any Video</p>
</div>
""", unsafe_allow_html=True)

# Input card

st.markdown(
    '<div class="input-heading">Paste YouTube URL or upload a video</div>',
    unsafe_allow_html=True
)

# Input method selection
input_method = st.radio(
    "Select input method",
    ["YouTube URL", "Upload Video"],
    horizontal=True,
    label_visibility="collapsed",
    key="input_method"
)

source = None

if input_method == "YouTube URL":
    st.markdown('<span class="input-label">YouTube Video URL</span>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
        key="url_input"
    )
else:
    st.markdown('<span class="input-label">Upload Video File</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=["mp4", "avi", "mov", "mkv", "flv", "wmv"],
        label_visibility="collapsed",
        key="video_upload"
    )
    source = uploaded_file

# Language input
st.markdown('<span class="input-label">Language (optional)</span>', unsafe_allow_html=True)
language = st.text_input(
    "Language",
    value="english",
    placeholder="e.g., english, spanish, french, hindi, etc.",
    label_visibility="collapsed",
    key="language_input"
)

# Process button
process_clicked = st.button("Process", use_container_width=True, key="process_btn")

st.markdown('</div>', unsafe_allow_html=True)

# Process transcript when user clicks Process
if process_clicked:
    if source is None or not source.strip():
        if input_method == "YouTube URL":
            st.error("Please enter a valid YouTube URL")
        else:
            st.error("Please upload a video file")
    else:
        try:
            # Handle uploaded file
            source_path = source
            if input_method == "Upload Video":
                # Save uploaded file to temporary location
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    source_path = tmp_file.name
            
            # Progress tracking
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # Define progress callback
            def on_progress(step: int, total: int, message: str):
                """Called by transcript_pipeline to update progress"""
                percent = int((step / total) * 100)
                progress_placeholder.progress(percent, text=f"{percent}%")
                status_placeholder.text(message)
            
            # Call transcript_pipeline with progress callback and language
            transcript = transcript_pipeline(source_path, language=language, progress_callback=on_progress)
            
            # Clear progress display
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Clean up temporary file if it was created
            if input_method == "Upload Video":
                try:
                    os.unlink(source_path)
                except:
                    pass
            
            # Update session state with new transcript and clear previous results
            st.session_state.current_transcript = transcript
            st.session_state.summary_result = None
            st.session_state.notes_result = None
            st.session_state.rag_chain = None
            st.session_state.chat_history = []
            st.session_state.selected_choice = None
            st.session_state.last_source = str(source)
            
            st.success("✓ Transcript processed successfully")
        
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")

# Show feature cards and selection only after transcript is ready
if st.session_state.current_transcript:
    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
    st.markdown("### Choose how to analyze the video")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3 class="feature-title">Summary</h3>
            <p class="feature-desc">Get a concise overview of the key points and main ideas from the video.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Summary", use_container_width=True, key="btn_summary"):
            st.session_state.selected_choice = "summary"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3 class="feature-title">Notes</h3>
            <p class="feature-desc">Structured notes with detailed information organized for quick reference.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Notes", use_container_width=True, key="btn_notes"):
            st.session_state.selected_choice = "notes"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3 class="feature-title">RAG Chatbot</h3>
            <p class="feature-desc">Ask questions and get accurate answers based on the video transcript.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask Questions", use_container_width=True, key="btn_rag"):
            st.session_state.selected_choice = "rag"
            st.rerun()
    
    # Display results based on selected choice
    if st.session_state.selected_choice == "summary":
        
        # Generate summary only if not already generated
        if st.session_state.summary_result is None:
            with st.spinner("Generating summary..."):
                st.session_state.summary_result = pipeline(st.session_state.current_transcript, choice=1)
        
        result = st.session_state.summary_result
        
        st.subheader(result['title'])
        st.write(result['summary'])
        
        col1, col2 = st.columns(2)
        with col1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_content = f"{result['title']}\n\n{result['summary']}"
            st.download_button(
                label="⬇️ Download Summary",
                data=download_content,
                file_name=f"summary_{timestamp}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("← Back to Features", use_container_width=True, key="back_summary"):
                st.session_state.selected_choice = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.selected_choice == "notes":
        
        # Generate notes only if not already generated
        if st.session_state.notes_result is None:
            with st.spinner("Generating notes..."):
                st.session_state.notes_result = pipeline(st.session_state.current_transcript, choice=2)
        
        result = st.session_state.notes_result
        
        st.subheader(result['title'])
        st.markdown(result['notes'])
        
        col1, col2 = st.columns(2)
        with col1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_content = f"{result['title']}\n\n{result['notes']}"
            st.download_button(
                label="⬇️ Download Notes",
                data=download_content,
                file_name=f"notes_{timestamp}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("← Back to Features", use_container_width=True, key="back_notes"):
                st.session_state.selected_choice = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.selected_choice == "rag":
        
        # Build RAG chain only once
        if st.session_state.rag_chain is None:
            with st.spinner("Building knowledge base..."):
                result = pipeline(st.session_state.current_transcript, choice=3)
                st.session_state.rag_chain = result['chain']
        
        # Display chat interface
        st.subheader("Ask anything about the video")
        
        # Show chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message['role']):
                st.write(message['content'])
        

        # Chat input
        with st.container():
            user_question = st.chat_input("Your question...")

        if user_question:
            # Add user message to history and display
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_question
            })
            with st.chat_message('user'):
                st.write(user_question)
            
            # Get response from RAG chain
            with st.spinner("Thinking..."):
                response = ask_question(st.session_state.rag_chain, user_question)
            
            # Add assistant response to history and display
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            with st.chat_message('assistant'):
                st.write(response)

            st.rerun()

        # Download and back buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.session_state.chat_history:
                chat_text = "Chat History\n" + "="*50 + "\n\n"
                for msg in st.session_state.chat_history:
                    role = "You" if msg['role'] == 'user' else "Assistant"
                    chat_text += f"{role}:\n{msg['content']}\n\n---\n"
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="⬇️ Download Chat",
                    data=chat_text,
                    file_name=f"chat_history_{timestamp}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            if st.button("← Back to Features", use_container_width=True, key="back_rag"):
                st.session_state.selected_choice = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)