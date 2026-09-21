import streamlit as st
import pandas as pd
import io

# Question words to filter by
QUESTION_WORDS = [
    'who', 'what', 'where', 'when', 'why', 'how',
    'can', 'is', 'are', 'do', 'does', 'will'
]

st.set_page_config(page_title="SEO Content Questions Extractor", layout="wide")

st.title("SEO & GEO Content Questions Extractor")
st.markdown("Extract question-based queries from your data sources for content optimization.")

# Sidebar setup
st.sidebar.header("Configuration")
data_source = st.sidebar.selectbox(
    "Select Data Source",
    options=["GSC Export", "BigQuery (Coming Soon)"]
)

if data_source == "BigQuery (Coming Soon)":
    st.info("BigQuery integration is under development. Please use 'GSC Export' for now.")
else:
    # GSC Export Mode
    uploaded_file = st.sidebar.file_uploader("Upload GSC Export (CSV)", type=['csv'])

    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            # Find the query column. GSC exports usually use 'Top queries' or 'Query'
            query_col = None
            for col in df.columns:
                if 'query' in col.lower() or 'queries' in col.lower():
                    query_col = col
                    break
            
            if not query_col:
                # If we couldn't automatically find it, ask the user to select
                query_col = st.selectbox("Select the column containing the queries:", options=df.columns)
            else:
                st.success(f"Automatically detected query column: `{query_col}`")
                
            if query_col:
                st.subheader("Extracted Questions")
                
                # Filter logic: convert queries to lowercase and check if they contain any question word as a distinct word
                # Using regex word boundary \b to ensure we match whole words (e.g. 'is', not 'this')
                pattern = r'\b(?:' + '|'.join(QUESTION_WORDS) + r')\b'
                
                # Create a boolean mask
                mask = df[query_col].astype(str).str.lower().str.contains(pattern, regex=True, na=False)
                questions_df = df[mask].copy()
                
                # Display metrics
                col1, col2 = st.columns(2)
                col1.metric("Total Queries in File", len(df))
                col2.metric("Questions Extracted", len(questions_df))
                
                # Display dataframe
                st.dataframe(questions_df, use_container_width=True)
                
                # Download button
                if not questions_df.empty:
                    csv = questions_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Extracted Questions as CSV",
                        data=csv,
                        file_name="extracted_questions.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No questions found in the dataset based on the current filters.")

        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.info("Please upload a CSV file from Google Search Console to begin.")
