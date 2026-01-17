#!/usr/bin/env python3
"""
influencer_summary_enhanced.py

Enhanced version with strategic insights including:
- Best posting times
- Effective templates & hooks
- Thumbnail strategies
- Breakthrough posts analysis
"""
import sys
import os
import pandas as pd
import numpy as np
import re
from collections import Counter
from datetime import datetime

# --- Helpers ---------------------------------------------------------------

def parse_int_like(x):
    """Try to parse numeric values with commas or strings like '1.2k' to integer."""
    if x is None:
        return None
    if (isinstance(x, float) and np.isnan(x)) or (isinstance(x, str) and x.strip() == ""):
        return None
    try:
        if isinstance(x, (int, float, np.integer, np.floating)):
            return int(x)
    except Exception:
        pass
    s = str(x).strip()
    s = s.replace(',', '')
    m = re.match(r'^([0-9]*\.?[0-9]+)\s*([kKmMbB])?$', s)
    if m:
        try:
            val = float(m.group(1))
        except Exception:
            return None
        suffix = m.group(2)
        if suffix:
            if suffix.lower() == 'k':
                val = int(val * 1_000)
            elif suffix.lower() == 'm':
                val = int(val * 1_000_000)
            elif suffix.lower() == 'b':
                val = int(val * 1_000_000_000)
        return int(val)
    try:
        return int(float(s))
    except Exception:
        return None

def most_common_string(series, top_n=1):
    if series is None:
        return None
    vals = [str(x).strip() for x in series.dropna().astype(str) if str(x).strip() and str(x).strip().lower() not in ['nan','none','nan.0','']]
    if not vals:
        return None
    c = Counter(vals)
    return [v for v,_ in c.most_common(top_n)]

def split_hashtags(cell):
    if cell is None:
        return []
    if (isinstance(cell, float) and np.isnan(cell)):
        return []
    s = str(cell)
    toks = re.split(r'[,\s;]+', s)
    toks = [t.lstrip('#').lower() for t in toks if t and t.strip() != '']
    return toks

def safe_mean(series):
    if series is None:
        return None
    try:
        ser = pd.to_numeric(series, errors='coerce').dropna()
        return float(ser.mean()) if len(ser) else None
    except Exception:
        return None

def pct_format(x):
    if x is None:
        return "N/A"
    try:
        return f"{x:.1f}%"
    except Exception:
        return str(x)

def parse_datetime(x):
    """Try to parse various datetime formats"""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    try:
        # Try common formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y %H:%M', '%m/%d/%Y', 
                    '%d-%m-%Y %H:%M:%S', '%d-%m-%Y', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']:
            try:
                return datetime.strptime(str(x).strip(), fmt)
            except:
                continue
        return pd.to_datetime(x)
    except:
        return None

def analyze_posting_times(g):
    """Analyze best posting times from timestamps"""
    time_cols = ['posted_at', 'timestamp', 'post_time', 'date', 'published_at']
    timestamps = []
    
    for col in time_cols:
        if col in g.columns:
            for val in g[col].dropna():
                dt = parse_datetime(val)
                if dt:
                    timestamps.append(dt)
    
    if not timestamps:
        return None
    
    # Get hour distribution
    hours = [dt.hour for dt in timestamps]
    hour_counter = Counter(hours)
    
    if not hour_counter:
        return None
    
    # Get top 2 posting hours
    top_hours = [h for h, _ in hour_counter.most_common(2)]
    
    # Convert to readable format
    time_ranges = []
    for hour in top_hours:
        if 5 <= hour < 12:
            time_ranges.append(f"morning ({hour}:00)")
        elif 12 <= hour < 17:
            time_ranges.append(f"afternoon ({hour}:00)")
        elif 17 <= hour < 21:
            time_ranges.append(f"evening ({hour}:00)")
        else:
            time_ranges.append(f"night ({hour}:00)")
    
    return time_ranges

def analyze_top_performers(g):
    """Find breakthrough posts with highest engagement"""
    # Calculate engagement score for each post
    g = g.copy()
    
    # Try to create engagement score
    engagement_scores = []
    for idx, row in g.iterrows():
        score = 0
        if 'likes' in row and pd.notna(row['likes']):
            likes = parse_int_like(row['likes'])
            if likes:
                score += likes
        if 'views' in row and pd.notna(row['views']):
            views = parse_int_like(row['views'])
            if views:
                score += views * 0.1  # Weight views less than likes
        if 'comments' in row and pd.notna(row['comments']):
            comments = parse_int_like(row['comments'])
            if comments:
                score += comments * 5  # Weight comments more
        if 'shares' in row and pd.notna(row['shares']):
            shares = parse_int_like(row['shares'])
            if shares:
                score += shares * 10  # Weight shares heavily
        
        engagement_scores.append(score)
    
    if not any(engagement_scores):
        return None
    
    g['engagement_score'] = engagement_scores
    
    # Get top 3 performing posts
    top_posts = g.nlargest(3, 'engagement_score')
    
    top_info = []
    for _, post in top_posts.iterrows():
        info = {}
        if 'content_template' in post and pd.notna(post['content_template']):
            info['template'] = str(post['content_template'])
        if 'hook_statement' in post and pd.notna(post['hook_statement']):
            info['hook'] = str(post['hook_statement'])[:80]  # Truncate long hooks
        if 'thumbnail_style' in post and pd.notna(post['thumbnail_style']):
            info['thumbnail'] = str(post['thumbnail_style'])
        if 'video_format' in post and pd.notna(post['video_format']):
            info['format'] = str(post['video_format'])
        
        # Get engagement metrics
        if 'likes' in post and pd.notna(post['likes']):
            info['likes'] = parse_int_like(post['likes'])
        if 'views' in post and pd.notna(post['views']):
            info['views'] = parse_int_like(post['views'])
        
        if info:
            top_info.append(info)
    
    return top_info if top_info else None

def analyze_thumbnails(g):
    """Analyze thumbnail strategies"""
    thumb_cols = ['thumbnail_style', 'thumbnail_type', 'thumbnail', 'cover_image_style']
    
    for col in thumb_cols:
        if col in g.columns:
            thumbs = most_common_string(g[col], top_n=3)
            if thumbs:
                return thumbs
    return None

def analyze_hooks(g):
    """Analyze effective hook statements"""
    hook_cols = ['hook_statement', 'hook', 'opening_line', 'caption_hook']
    
    for col in hook_cols:
        if col in g.columns:
            # Get non-empty hooks
            hooks = [str(x).strip() for x in g[col].dropna().astype(str) 
                    if str(x).strip() and len(str(x).strip()) > 5 
                    and str(x).strip().lower() not in ['nan','none','n/a']]
            if hooks:
                # Return top 2-3 most common hooks (truncated)
                counter = Counter(hooks)
                return [h[:100] for h, _ in counter.most_common(2)]
    return None

# --- Core summary generation -----------------------------------------------

def summarize_influencer(df, handle_col='handle'):
    summaries = []
    # Ensure handle column exists
    if handle_col not in df.columns:
        if 'id' in df.columns:
            df['handle'] = df['id']
        else:
            df['handle'] = "unknown_handle"

    for handle, g in df.groupby('handle', dropna=False):
        # influencer-level
        platform = (most_common_string(g.get('platform')) or ["unknown platform"])[0]
        real_name = (most_common_string(g.get('real_name')) or [handle])[0]
        category = (most_common_string(g.get('category')) or ["creator"])[0]

        # followers: take the max observed followers_at_time
        follower_vals_raw = pd.Series(g.get('followers_at_time')) if 'followers_at_time' in g else pd.Series(dtype=object)
        follower_vals = [parse_int_like(x) for x in follower_vals_raw.dropna().unique()] if not follower_vals_raw.empty else []
        followers = max([v for v in follower_vals if v is not None], default=None)

        # posts count
        post_count = len(g)

        # basic metrics
        avg_engagement = safe_mean(g.get('engagement_rate'))
        avg_likes = safe_mean(g.get('likes'))
        avg_views = safe_mean(g.get('views'))
        avg_comments = safe_mean(g.get('comments'))
        avg_retention = safe_mean(g.get('retention_pct'))
        avg_watch_time = safe_mean(g.get('watch_time_seconds'))
        avg_view_duration = safe_mean(g.get('avg_view_duration_seconds'))

        # content patterns
        top_templates = most_common_string(g.get('content_template'), top_n=2) or []
        top_video_format = most_common_string(g.get('video_format')) or []
        predominant_orientation = most_common_string(g.get('orientation')) or []
        top_editing = most_common_string(g.get('editing_style')) or []

        # CTA presence frequency
        cta_vals = g.get('cta_present')
        cta_yes = 0
        if cta_vals is not None:
            try:
                cta_series = cta_vals.dropna().astype(str).str.lower()
                cta_yes = cta_series.apply(lambda s: s in ['yes','true','1','y','t']).sum()
            except Exception:
                cta_yes = 0
        cta_freq_pct = (cta_yes / post_count * 100) if post_count else None

        # hashtags and keywords
        hashtags_series = g.get('hashtags')
        hashtags_all = []
        if hashtags_series is not None:
            for cell in hashtags_series.dropna().astype(str):
                hashtags_all.extend(split_hashtags(cell))
        top_hashtags = [h for h,_ in Counter(hashtags_all).most_common(5)]

        topic_keywords_series = g.get('topic_keywords')
        topics_all = []
        if topic_keywords_series is not None:
            for cell in topic_keywords_series.dropna().astype(str):
                toks = re.split(r'[,\|;]+', cell)
                toks = [t.strip().lower() for t in toks if t.strip()]
                topics_all.extend(toks)
        top_topics = [t for t,_ in Counter(topics_all).most_common(5)]

        # sentiment
        sentiments = []
        sersent = g.get('sentiment')
        if sersent is not None:
            for v in sersent.dropna().astype(str):
                v_low = v.strip().lower()
                try:
                    sentiments.append(float(v_low))
                    continue
                except Exception:
                    pass
                if v_low in ['positive','pos','p','+','1']:
                    sentiments.append(1.0)
                elif v_low in ['neutral','neu','0','0.0']:
                    sentiments.append(0.0)
                elif v_low in ['negative','neg','-','-1']:
                    sentiments.append(-1.0)
        avg_sentiment = (sum(sentiments)/len(sentiments)) if sentiments else None

        # NEW: Advanced insights
        best_times = analyze_posting_times(g)
        top_performers = analyze_top_performers(g)
        thumbnail_styles = analyze_thumbnails(g)
        effective_hooks = analyze_hooks(g)

        # assemble paragraph (now 5-6 lines with strategic insights)
        s1_followers = f"{followers:,}" if followers is not None else "an unknown number of"
        s1 = (f"The {real_name} ({handle}) is a {category} on {platform} with {s1_followers} followers and "
              f"has {post_count} posts in the dataset.")

        perf_parts = []
        if avg_views is not None:
            perf_parts.append(f"avg views ≈ {int(avg_views):,}")
        if avg_likes is not None:
            perf_parts.append(f"avg likes ≈ {int(avg_likes):,}")
        if avg_engagement is not None:
            try:
                if avg_engagement > 1.5:
                    perf_parts.append(f"avg engagement ≈ {avg_engagement:.2f}%")
                else:
                    perf_parts.append(f"avg engagement ≈ {avg_engagement:.3f}")
            except Exception:
                perf_parts.append(f"avg engagement ≈ {avg_engagement}")
        if perf_parts:
            s2 = "Performance: " + "; ".join(perf_parts) + "."
        else:
            s2 = "Performance: no numeric engagement data available."

        content_insights = []
        if top_templates:
            content_insights.append(f"often uses template(s) {', '.join(top_templates)}")
        if top_video_format:
            content_insights.append(f"prefers format {top_video_format[0]}")
        if top_hashtags:
            content_insights.append(f"common hashtags: #{', #'.join(top_hashtags[:3])}")
        if top_topics:
            content_insights.append(f"topics: {', '.join(top_topics[:3])}")
        if avg_retention is not None:
            content_insights.append(f"retention ~ {pct_format(avg_retention)}")
        if cta_freq_pct is not None:
            content_insights.append(f"CTA in {cta_freq_pct:.0f}% of posts")
        if content_insights:
            s3 = "Content & strategy: " + "; ".join(content_insights) + "."
        else:
            s3 = "Content & strategy: not enough structured content data to infer patterns."

        # NEW: Strategic insights paragraph
        strategic_parts = []
        
        if best_times:
            strategic_parts.append(f"Best posting times: {' and '.join(best_times)}")
        
        if effective_hooks:
            hook_preview = effective_hooks[0][:60] + "..." if len(effective_hooks[0]) > 60 else effective_hooks[0]
            strategic_parts.append(f"Effective hooks include: '{hook_preview}'")
        
        if thumbnail_styles:
            strategic_parts.append(f"Thumbnail strategies: {', '.join(thumbnail_styles[:2])} work well")
        
        if top_performers:
            # Describe breakthrough posts
            best_post = top_performers[0]
            breakthrough = []
            if 'template' in best_post:
                breakthrough.append(f"using {best_post['template']} template")
            if 'views' in best_post:
                breakthrough.append(f"reaching {best_post['views']:,} views")
            if breakthrough:
                strategic_parts.append(f"Top-performing post: {' '.join(breakthrough)}")
        
        if strategic_parts:
            s4 = "Strategic insights: " + "; ".join(strategic_parts) + "."
        else:
            s4 = "Strategic insights: analyze individual post performance to identify breakthrough patterns."

        rec_parts = []
        if avg_engagement is not None:
            try:
                if avg_engagement < 0.01:
                    rec_parts.append("Consider stronger hooks / CTAs to boost engagement.")
            except Exception:
                pass
        if avg_retention is not None and avg_retention < 30:
            rec_parts.append("Shorten videos or front-load value to improve retention.")
        if avg_sentiment is not None and avg_sentiment < 0:
            rec_parts.append("Audience sentiment trends negative — evaluate tone.")
        
        if top_performers and len(top_performers) > 0:
            rec_parts.append("Replicate successful elements from top-performing posts to boost profile growth and maintain momentum.")
        
        if not rec_parts:
            rec = "Overall: consistent posting; continue monitoring top-performing templates and experiment with proven formats."
        else:
            rec = "Recommendation: " + " ".join(rec_parts)

        paragraph = "\n".join([s1, s2, s3, s4, rec])
        summaries.append((handle, paragraph))
    return summaries

# --- Main ---------------------------------------------

def main(csv_path):
    # read with pandas; treat empty strings as NaN
    df = pd.read_csv(csv_path, dtype=str, na_values=['', 'NA', 'N/A', 'nan'])
    # normalize column names (strip spaces)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # quick mapping: if a column contains 'engagement' in header, rename to engagement_rate
    if 'engagement_rate' not in [c.lower() for c in df.columns]:
        for c in df.columns:
            if 'engagement' in str(c).lower() or 'likes+comments' in str(c).lower() or ('likes' in str(c).lower() and 'followers' in str(c).lower() and '=' in str(c)):
                df.rename(columns={c: 'engagement_rate'}, inplace=True)
                break

    # ensure expected columns exist (create as empty if missing)
    expected = ['platform','real_name','category','followers_at_time','engagement_rate','likes','views','comments','shares',
                'retention_pct','watch_time_seconds','avg_view_duration_seconds','content_template','video_format',
                'orientation','editing_style','cta_present','hashtags','topic_keywords','sentiment','handle','id',
                'posted_at','timestamp','post_time','date','published_at','hook_statement','hook','opening_line',
                'caption_hook','thumbnail_style','thumbnail_type','thumbnail','cover_image_style']
    for col in expected:
        if col not in df.columns:
            df[col] = np.nan

    summaries = summarize_influencer(df, handle_col='handle')

    out_file = "new_insta_summary8.txt"
    with open(out_file, 'w', encoding='utf-8') as f:
        for handle, para in summaries:
            f.write(para + "\n\n")
            print("=" * 80)
            print(para)
            print("=" * 80 + "\n")

    print(f"\nSaved all enhanced summaries to {out_file}")

# ★★★★★ FINAL SECTION — INPUT PATH HARDCODED ★★★★★
if __name__ == '__main__':
    # ★ Put your CSV file path here ★
    csv_path = r"D:\QDATA1\insta_influencer_n8.csv" # <-- CHANGE THIS to your CSV file path

    if not os.path.isfile(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)
    main(csv_path)