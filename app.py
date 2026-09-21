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
        st.sidebar.subheader("Advanced Filters")
        
        # Define default keywords based on user sample
        default_brand = "pep, paxi, foneyam, capfin, plus more"
        default_competitors = "ackermans, shoprite, pick n pay, mr price"
        
        brand_input = st.sidebar.text_area("Brand Keywords (comma-separated)", value=default_brand)
        brand_kw = [k.strip().lower() for k in brand_input.split(',')] if brand_input else []
        brand_filter = st.sidebar.radio("Brand Filter", ["Show All", "Brand Only", "Non-Brand Only"])

        comp_input = st.sidebar.text_area("Competitor Keywords (comma-separated)", value=default_competitors)
        comp_kw = [k.strip().lower() for k in comp_input.split(',')] if comp_input else []
        comp_filter = st.sidebar.radio("Competitor Filter", ["Show All", "Competitors Only", "Exclude Competitors"])

        custom_input = st.sidebar.text_input("Custom 'Must Include' Keywords", help="e.g. samsung, dstv, router")
        custom_kw = [k.strip().lower() for k in custom_input.split(',')] if custom_input else []

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
                
                # 1. Base Question Filter
                pattern = r'\b(?:' + '|'.join(QUESTION_WORDS) + r')\b'
                q_mask = df[query_col].astype(str).str.lower().str.contains(pattern, regex=True, na=False)
                
                # 2. Brand Filter
                brand_pattern = '|'.join([f"\\b{k}\\b" for k in brand_kw]) if brand_kw else r'(?!x)x'
                has_brand = df[query_col].astype(str).str.lower().str.contains(brand_pattern, regex=True, na=False)
                if brand_filter == "Brand Only":
                    q_mask = q_mask & has_brand
                elif brand_filter == "Non-Brand Only":
                    q_mask = q_mask & ~has_brand

                # 3. Competitor Filter
                comp_pattern = '|'.join([f"\\b{k}\\b" for k in comp_kw]) if comp_kw else r'(?!x)x'
                has_comp = df[query_col].astype(str).str.lower().str.contains(comp_pattern, regex=True, na=False)
                if comp_filter == "Competitors Only":
                    q_mask = q_mask & has_comp
                elif comp_filter == "Exclude Competitors":
                    q_mask = q_mask & ~has_comp

                # 4. Custom Keywords Filter
                if custom_kw:
                    custom_pattern = '|'.join([f"\\b{k}\\b" for k in custom_kw])
                    has_custom = df[query_col].astype(str).str.lower().str.contains(custom_pattern, regex=True, na=False)
                    q_mask = q_mask & has_custom

                questions_df = df[q_mask].copy()
                
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

