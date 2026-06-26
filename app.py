import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="카페 고객 피드백 대시보드",
    page_icon="☕",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 3.5rem; padding-bottom: 1rem; }

    .main-title { font-size: 1.9rem; font-weight: 800; color: #1a1a1a; margin-bottom: 2px; }
    .sub-title   { font-size: 0.88rem; color: #888; margin-bottom: 0; }
    .section-label {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em;
        text-transform: uppercase; color: #999; margin: 20px 0 10px;
    }

    /* ── 유형 카드 ── */
    .m-card {
        border-radius: 14px; padding: 22px 16px 18px;
        text-align: center; color: white;
    }
    .m-num   { font-size: 2.8rem; font-weight: 900; line-height: 1; }
    .m-label { font-size: 1.05rem; margin-top: 6px; opacity: 0.93; font-weight: 600; }
    .m-sub   { font-size: 0.78rem; opacity: 0.75; margin-top: 3px; }

    /* ── 긴급 카드 ── */
    .u-card {
        background: #fff8f8;
        border: 1.8px solid #fca5a5;
        border-radius: 14px;
        padding: 18px 18px 16px;
        height: 100%;
    }
    .u-rank {
        display: inline-block;
        background: #ef4444; color: white;
        font-size: 0.7rem; font-weight: 700;
        border-radius: 99px; padding: 2px 10px;
        margin-bottom: 10px; letter-spacing: 0.05em;
    }
    .u-meta {
        font-size: 0.78rem; color: #aaa; margin-bottom: 8px;
    }
    .u-meta b { color: #666; }
    .u-content {
        font-size: 0.93rem; line-height: 1.6; color: #222;
        background: white; border-radius: 8px;
        padding: 10px 12px; margin: 8px 0;
        border: 1px solid #f1f1f1;
    }
    .u-reason {
        font-size: 0.81rem; color: #b91c1c;
        background: #fef2f2; border-left: 3px solid #ef4444;
        padding: 6px 10px; border-radius: 0 6px 6px 0; margin-top: 8px;
    }

    div[data-testid="stHorizontalBlock"] > div { gap: 0.6rem !important; }
</style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ──────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("Day3_과제_feedback_v.2.csv", dtype=str)

df = load_data()

date_min = df["받은날짜"].min()
date_max = df["받은날짜"].max()

# ── 헤더 ─────────────────────────────────────────────────
st.markdown('<p class="main-title">☕ 카페 고객 피드백 대시보드</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="sub-title">총 {len(df)}건 &nbsp;·&nbsp; {date_min} – {date_max}</p>',
    unsafe_allow_html=True,
)
st.divider()


# ── 1. 유형별 카드 ────────────────────────────────────────
st.markdown('<p class="section-label">유형별 피드백 현황</p>', unsafe_allow_html=True)

counts = df["유형"].value_counts().to_dict()
TYPE_STYLE = {
    "불만": ("#ef4444", "📣", "부정 감정 위주"),
    "요청": ("#3b82f6", "💡", "개선 제안 포함"),
    "칭찬": ("#22c55e", "⭐", "긍정 감정 위주"),
    "문의": ("#f59e0b", "❓", "정보 확인 필요"),
}

cols = st.columns(4, gap="small")
for col, (label, (color, icon, desc)) in zip(cols, TYPE_STYLE.items()):
    with col:
        st.markdown(f"""
        <div class="m-card" style="background:{color};">
            <div class="m-num">{counts.get(label, 0)}</div>
            <div class="m-label">{icon} {label}</div>
            <div class="m-sub">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ── 2. 긴급 불만 TOP 3 ────────────────────────────────────
st.markdown('<p class="section-label">🚨 긴급 불만 TOP 3</p>', unsafe_allow_html=True)

KEYWORDS = {
    "오류": "앱·시스템 오류",
    "환불": "환불 요청",
    "기다": "대기 불만",
    "안 울": "진동벨 미작동",
    "잘못": "주문 오류",
}

def score_row(row):
    if row["유형"] != "불만":
        return 0, []
    score, reasons = 0, []
    if str(row["별점"]) == "1":
        score += 2
        reasons.append("별점 1점")
    for kw, label in KEYWORDS.items():
        if kw in str(row["내용"]):
            score += 1
            reasons.append(f"{label} ({kw!r})")
    return score, reasons

scored = []
for _, row in df.iterrows():
    s, r = score_row(row)
    if s > 0:
        scored.append({**row.to_dict(), "_score": s, "_reasons": r})

top3 = sorted(scored, key=lambda x: (-x["_score"], int(x["id"])))[:3]

if top3:
    cols = st.columns(len(top3), gap="small")
    rank_labels = ["🥇 1위", "🥈 2위", "🥉 3위"]
    for col, item, rank in zip(cols, top3, rank_labels):
        reasons_str = " &nbsp;·&nbsp; ".join(item["_reasons"])
        with col:
            st.markdown(f"""
            <div class="u-card">
                <span class="u-rank">{rank} 긴급</span>
                <div class="u-meta">
                    <b>ID #{item['id']}</b> &nbsp;·&nbsp;
                    경로 {item['경로']} &nbsp;·&nbsp;
                    별점 {item['별점']}
                </div>
                <div class="u-content">{item['내용']}</div>
                <div class="u-reason">⚡ {reasons_str}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("긴급 불만 항목이 없습니다.")
