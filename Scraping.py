
## scarping for the URL 
import instaloader
import pandas as pd
from datetime import datetime
import time
import re
from PIL import Image
import requests
from io import BytesIO
import statistics

class InstagramScraper:
    def __init__(self):
        self.L = instaloader.Instaloader()
        # Optional: Login to avoid rate limits (use a spare account)
        # self.L.login("your_username", "your_password")
        
        # Category keywords for auto-detection
        self.category_keywords = {
            'fitness': ['workout', 'gym', 'fitness', 'exercise', 'training', 'muscle'],
            'food': ['recipe', 'cooking', 'food', 'meal', 'delicious', 'tasty'],
            'fashion': ['outfit', 'style', 'fashion', 'ootd', 'wear', 'clothing'],
            'travel': ['travel', 'trip', 'vacation', 'explore', 'adventure', 'wanderlust'],
            'beauty': ['makeup', 'beauty', 'skincare', 'cosmetics', 'lipstick'],
            'tech': ['technology', 'tech', 'gadget', 'review', 'unboxing', 'device'],
            'business': ['entrepreneur', 'business', 'startup', 'marketing', 'sales'],
            'lifestyle': ['lifestyle', 'daily', 'life', 'routine', 'vlog']
        }
    
    def extract_username_from_url(self, url):
        """Extract Instagram username from profile URL"""
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Patterns to match Instagram URLs
        patterns = [
            r'instagram\.com/([^/?]+)',  # https://www.instagram.com/username
            r'instagr\.am/([^/?]+)',      # https://instagr.am/username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Remove any query parameters
                username = username.split('?')[0]
                return username
        
        # If no pattern matches, assume it's already a username
        return url
    
    def extract_hashtags(self, caption):
        """Extract hashtags from caption"""
        if not caption:
            return ""
        hashtags = re.findall(r'#\w+', caption)
        return ",".join(hashtags)
    
    def has_cta(self, caption):
        """Check if caption contains CTA keywords"""
        if not caption:
            return "No"
        cta_keywords = ['link in bio', 'click', 'shop', 'buy', 'visit', 'check out', 
                       'swipe up', 'dm me', 'comment below', 'tag', 'follow']
        caption_lower = caption.lower()
        return "Yes" if any(keyword in caption_lower for keyword in cta_keywords) else "No"
    
    def detect_category(self, caption, bio):
        """Auto-detect content category based on caption and bio"""
        if not caption and not bio:
            return "Unknown"
        
        text = f"{caption or ''} {bio or ''}".lower()
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get).capitalize()
        return "Lifestyle"
    
    def extract_hook_text(self, caption):
        """Extract the first sentence or first 100 chars as hook"""
        if not caption:
            return ""
        
        # Try to get first sentence
        sentences = re.split(r'[.!?]\s+', caption)
        if sentences:
            hook = sentences[0].strip()
            # Limit to 100 characters
            return hook[:100] + "..." if len(hook) > 100 else hook
        return ""
    
    def analyze_image_orientation(self, image_url):
        """Download and analyze image orientation"""
        try:
            response = requests.get(image_url, timeout=10)
            img = Image.open(BytesIO(response.content))
            width, height = img.size
            
            ratio = width / height
            
            if ratio > 1.2:
                return "Landscape"
            elif ratio < 0.8:
                return "Portrait"
            else:
                return "Square"
        except Exception as e:
            return "Unknown"
    
    def detect_thumbnail_style(self, image_url):
        """Analyze thumbnail style (basic color analysis)"""
        try:
            response = requests.get(image_url, timeout=10)
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get average brightness
            pixels = list(img.getdata())
            avg_brightness = sum(sum(pixel) for pixel in pixels) / (len(pixels) * 3)
            
            # Simple classification
            if avg_brightness > 180:
                return "Bright/Light"
            elif avg_brightness < 80:
                return "Dark/Moody"
            else:
                return "Balanced"
        except Exception as e:
            return "Unknown"
    
    def detect_guest_presence(self, caption):
        """Detect if post mentions guests or collaborations"""
        if not caption:
            return "No"
        
        guest_keywords = ['featuring', 'with @', 'guest', 'collab', 'collaboration', 
                         'interview', 'joined by', 'special guest']
        caption_lower = caption.lower()
        
        # Also check for @ mentions (excluding self)
        mentions = re.findall(r'@\w+', caption)
        
        if any(keyword in caption_lower for keyword in guest_keywords) or len(mentions) > 2:
            return "Yes"
        return "No"
    
    def detect_content_template(self, caption, video_format):
        """Detect content template/format"""
        if not caption:
            return "Unknown"
        
        caption_lower = caption.lower()
        
        # Common templates
        if any(word in caption_lower for word in ['tutorial', 'how to', 'step by step']):
            return "Tutorial"
        elif any(word in caption_lower for word in ['review', 'unboxing', 'testing']):
            return "Review"
        elif any(word in caption_lower for word in ['before and after', 'transformation']):
            return "Before/After"
        elif any(word in caption_lower for word in ['day in', 'routine', 'vlog']):
            return "Vlog/Routine"
        elif any(word in caption_lower for word in ['tips', 'advice', 'hacks']):
            return "Tips/Advice"
        elif video_format == "Reel" and len(caption_lower) < 50:
            return "Short-form Entertainment"
        else:
            return "General Content"
    
    def detect_editing_style(self, video_duration, caption):
        """Detect editing style based on duration and content"""
        if not video_duration:
            return "N/A (Image)"
        
        caption_lower = (caption or "").lower()
        
        # Fast-paced content indicators
        fast_indicators = ['quick', 'fast', 'rapid', 'tips', 'hacks']
        has_fast_indicators = any(word in caption_lower for word in fast_indicators)
        
        if video_duration < 15 and has_fast_indicators:
            return "Fast-paced/Jump cuts"
        elif video_duration < 30:
            return "Dynamic/Quick cuts"
        elif video_duration < 60:
            return "Moderate pacing"
        else:
            return "Slow/Cinematic"
    
    def detect_meme_template(self, caption):
        """Detect if using popular meme templates"""
        if not caption:
            return "No"
        
        meme_indicators = ['pov:', 'when you', 'nobody:', 'me:', 'literally', 
                          'that moment when', 'expectation vs reality']
        caption_lower = caption.lower()
        
        if any(indicator in caption_lower for indicator in meme_indicators):
            return "Yes"
        return "No"
    
    def get_timezone_from_profile(self, profile):
        """Estimate timezone from profile location"""
        if hasattr(profile, 'biography') and profile.biography:
            bio_lower = profile.biography.lower()
            
            # Common timezone indicators
            if any(word in bio_lower for word in ['los angeles', 'la', 'california', 'pacific']):
                return "PST/PDT"
            elif any(word in bio_lower for word in ['new york', 'ny', 'eastern']):
                return "EST/EDT"
            elif any(word in bio_lower for word in ['london', 'uk', 'britain']):
                return "GMT/BST"
            elif any(word in bio_lower for word in ['india', 'mumbai', 'delhi']):
                return "IST"
        
        return "Unknown"
    
    def calculate_avg_content_length(self, posts_data):
        """Calculate average video duration trend"""
        durations = [p['video_duration_seconds'] for p in posts_data 
                    if p.get('video_duration_seconds') and p['video_duration_seconds'] != '']
        
        if durations:
            avg = statistics.mean([float(d) for d in durations])
            return f"{avg:.1f}s"
        return "N/A"
    
    def scrape_profile(self, url_or_handle, max_posts=50):
        """Scrape data from a single Instagram profile using URL or username"""
        # Extract username from URL if needed
        handle = self.extract_username_from_url(url_or_handle)
        
        print(f"\n🔍 Scraping @{handle}...")
        
        try:
            profile = instaloader.Profile.from_username(self.L.context, handle)
            
            data = []
            post_count = 0
            
            # Get profile info
            followers = profile.followers
            bio = profile.biography
            timezone = self.get_timezone_from_profile(profile)
            
            # Iterate through posts
            for post in profile.get_posts():
                if post_count >= max_posts:
                    break
                
                try:
                    # Calculate engagement rate
                    likes = post.likes
                    comments = post.comments
                    engagement_rate = ((likes + comments) / followers) * 100 if followers > 0 else 0
                    
                    # Determine video format
                    if post.is_video:
                        video_format = "Reel" if post.typename == "GraphVideo" else "Video"
                    else:
                        video_format = "Image/Carousel"
                    
                    # Get image URL for analysis
                    image_url = post.url
                    
                    # Detect category
                    category = self.detect_category(post.caption, bio)
                    
                    # Get orientation (with rate limiting)
                    orientation = self.analyze_image_orientation(image_url) if post_count < 10 else "Unknown"
                    
                    # Get thumbnail style (with rate limiting)
                    thumbnail_style = self.detect_thumbnail_style(image_url) if post_count < 10 else "Unknown"
                    
                    # Extract data
                    row = {
                        'id': f"{handle}_{post.shortcode}",
                        'platform': 'Instagram',
                        'handle': handle,
                        'real_name': profile.full_name,
                        'category': category,
                        'followers_at_time': followers,
                        'post_url': f"https://www.instagram.com/p/{post.shortcode}/",
                        'post_datetime_utc': post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                        'timezone': timezone,
                        'video_format': video_format,
                        'video_duration_seconds': post.video_duration if post.is_video else '',
                        'orientation': orientation,
                        'Average time of content length trend': '',  # Will be filled after all posts
                        'views': post.video_view_count if post.is_video else '',
                        'likes': likes,
                        'comments': comments,
                        'shares': 'N/A (Not public)',  # Instagram doesn't expose share counts
                        'engagement_rate': f"{engagement_rate:.2f}%",
                        'thumbnail_style': thumbnail_style,
                        'hook_text': self.extract_hook_text(post.caption),
                        'caption_text': post.caption if post.caption else '',
                        'hashtags': self.extract_hashtags(post.caption),
                        'cta_present': self.has_cta(post.caption),
                        'guest_present': self.detect_guest_presence(post.caption),
                        'content_template': self.detect_content_template(post.caption, video_format),
                        'editing_style': self.detect_editing_style(post.video_duration if post.is_video else None, post.caption),
                        'meme_template': self.detect_meme_template(post.caption),
                        'audio_used': 'N/A (Not available via API)',  # Instaloader can't access audio info
                        'notes': '',  # For manual notes
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    data.append(row)
                    post_count += 1
                    print(f"  ✓ Scraped post {post_count}/{max_posts}")
                    
                    # Rate limiting - be nice to Instagram
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"  ⚠️ Error scraping post: {str(e)}")
                    continue
            
            # Calculate average content length trend
            avg_length = self.calculate_avg_content_length(data)
            for row in data:
                row['Average time of content length trend'] = avg_length
            
            print(f"✅ Completed @{handle}: {post_count} posts collected")
            return data
             
        except Exception as e:
            print(f"❌ Error scraping @{handle}: {str(e)}")
            return []
        
    def scrape_multiple_profiles(self, urls_or_handles, max_posts_per_profile=50):
        """Scrape multiple profiles and combine data"""
        all_data = []
        
        for url_or_handle in urls_or_handles:
            profile_data = self.scrape_profile(url_or_handle, max_posts_per_profile)
            all_data.extend(profile_data)
            
            # Longer pause between profiles to avoid rate limits
            print("⏳ Cooling down for 10 seconds...")
            time.sleep(10)
        
        return all_data
    
    def save_to_csv(self, data, filename='instagram_data.csv'):
        """Save collected data to CSV"""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Data saved to {filename}")
        print(f"📊 Total posts collected: {len(df)}")
        
        # Print summary
        print("\n📈 Data Summary:")
        print(f"   • Categories detected: {df['category'].nunique()}")
        print(f"   • Posts with CTA: {(df['cta_present'] == 'Yes').sum()}")
        print(f"   • Posts with guests: {(df['guest_present'] == 'Yes').sum()}")
        print(f"   • Meme templates: {(df['meme_template'] == 'Yes').sum()}")


# ==================== HOW TO USE ====================

if __name__ == "__main__":
    # Initialize scraper
    scraper = InstagramScraper()
    
    # YOUR INFLUENCER LIST - NOW SUPPORTS URLS!
    # You can use either full URLs or just usernames
    influencer_urls = [
        " profile URL"
        ,
        
        # You can also mix URLs and usernames:
        # 'rajshamani',  # Just username works too!
    ]
    
    # Scrape data (adjust max_posts as needed)
    print("🚀 Starting Enhanced Instagram data collection...")
    print(f"📋 Profiles to scrape: {len(influencer_urls)}")
    print("\n⚠️ Note: Image analysis (orientation, thumbnail) is limited to first 10 posts")
    print("   to avoid excessive API calls. Adjust in code if needed.\n")
    
    data = scraper.scrape_multiple_profiles(
        urls_or_handles=influencer_urls,
        max_posts_per_profile=50  # Adjust this number
    )
    
    # Save to CSV
    if data:
        scraper.save_to_csv(data, 'insta_influencer.csv') ## output file
        print("\n✨ Scraping complete!")
    else:
        print("\n⚠️ No data collected. Check errors above.")


