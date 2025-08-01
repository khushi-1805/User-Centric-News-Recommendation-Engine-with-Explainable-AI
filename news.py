import streamlit as st 
import requests
import random
from datetime import datetime, timedelta
import google.generativeai as genai
import openai




API_KEY = "bb547c2210d24e2796b0dec0bcbf08cc"
BASE_URL = "https://newsapi.org/v2/everything"
PERPLEXITY_API_KEY = "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"
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

def perplexity_generate_insight(title, desc, interest):
    prompt = f"""
Khushi is a BTech AI student who is curious about {interest}.
She just read this news:

Title: {title}
Description: {desc}

Explain it to her in a friendly and simple way. Break it into 3 clear points:

1. **Why should Khushi care about this news?** (Make it personal to her interest in {interest}.)
2. **What does this mean for her future?** (Explain any positive or negative effects on her career, learning, or awareness.)
3. **What can she do about it right now?** (Give practical steps—if it's useful, how to use it; if risky, how to stay cautious.)

Keep the tone casual and helpful, like you are advising a friend. Each point can be 2-3 sentences long.
"""

    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",  # Or sonar-small-chat, sonar-medium-chat
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{PERPLEXITY_BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Couldn't generate insight right now: {str(e)}"


use_perplexity=True


all_interests = [
"AI", "machine learning", "data science", "startups",
"women empowerment", "mental health", "education", "Digital India",
"climate change", "job market", "internships", "rural development",
"quantum computing", "inflation", "technology", "sustainability"
]

impact_reasons = {
"AI": "Keep up with cutting-edge tech shifts.",
"startups": "Great for entrepreneurship mindset.",
"climate change": "Critical for a sustainable future.",
"rural development": "Useful for inclusive innovation.",
"mental health": "Matters for wellbeing in high-pressure careers.",
}

st.set_page_config(page_title="Smart News Recommender", layout="wide")



st.markdown(
    "<h1 style='text-align: center; color:rgb(138, 240, 246);'> Personalized News Recommender</h1>",
    unsafe_allow_html=True
)
st.markdown("<p style='text-align: center;'>Get AI-powered insights on the news you care about!</p>", unsafe_allow_html=True)

left_col, middle_col,  = st.columns([1, 2])

with left_col:
    st.subheader("📌 Categories")

    # Show all interests as a list of checkboxes
    selected_interests = []
    for interest in all_interests:
        if st.checkbox(interest, key=interest):
            selected_interests.append(interest)


if selected_interests:  # now it's a list
    from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    recommended_articles = []
   


    for interest in selected_interests:
      if len(recommended_articles) >= 20:
        break

      params = {
      "q": interest,
      "from": from_date,
      "sortBy": "relevancy",
      "language": "en",
      "pageSize": 5,
      "apiKey": API_KEY
      }

      response = requests.get(BASE_URL, params=params)
      if response.status_code != 200:
        st.warning(f"Failed to fetch for {interest}")
        continue

      articles = response.json().get("articles", [])
      random.shuffle(articles)

      for article in articles:
        if article.get("title") and article.get("description"):
          if interest not in [a["matched_interest"] for a in recommended_articles]:
            recommended_articles.append({
      "title": article["title"],
      "url": article["url"],
      "matched_interest": interest,
      "description": article["description"],
      "publishedAt": article["publishedAt"],
      "source": article["source"]["name"],
      "reason": impact_reasons.get(interest, "Relevant to your interests.")
      })
            break


    if recommended_articles:
        if "selected_article" not in st.session_state:
            st.session_state.selected_article = recommended_articles[0]

        # Middle Column (Full Article View)
        with middle_col:
            a = st.session_state.selected_article
            st.markdown(f"### {a['title']}")
            if "urlToImage" in a and a["urlToImage"]:
              st.image(a["urlToImage"], use_container_width=True)
            else:
              st.image("https://via.placeholder.com/600x300?text=No+Image", use_container_width=True)


            with st.spinner("🤖 Generating detailed insight..."):
                insight = perplexity_generate_insight(a['title'], a['description'], a['matched_interest'])
            st.markdown(
                      f"""
                      <div style="
                          padding:10px; 
                          border-radius:5px;
                          font-size:32px; 
                          color:white; 
                          border: 2px solid rgb(138, 240, 246);
                          border-radius: 10px;
                          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                          margin-bottom:20px;">
                          {insight}
                      </div>
                      """,
                      unsafe_allow_html=True
                  )
            st.markdown(
              f"""
              <div style="
                  padding:10px; 
                  border-radius:5px;
                  font-size:32px; 
                  color:white; 
                  ">
                  📝 {a['description']}
              </div>
              """,
              unsafe_allow_html=True
          )
            st.markdown(
                f"""
                <div style="
                    padding:10px; 
                    border-radius:5px;
                    font-size:32px; 
                    color:white; 
                    ">
                    📅 {a['publishedAt']} | 🗞️ Source: {a['source']}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div style="
                    padding:10px; 
                    border-radius:5px;
                    font-size:32px; 
                    links:underline;
                    color:white; 
                    ">
                    🔗 [Read Full Article]({a['url']})                </div>
                """,
                unsafe_allow_html=True
            )
           
            st.markdown(f"🔗 [Read Full Article]({a['url']})")

            

    


   
   

