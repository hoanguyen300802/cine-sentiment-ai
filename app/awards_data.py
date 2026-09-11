"""
Awards and Hall of Fame Data Catalog for CineSentiment AI.
Curated directory of prestigious film, festival, and television awards.
"""

AWARDS_CATALOG = [
    {
        'id': 'oscars',
        'slug': 'oscars',
        'name': 'Academy Awards (The Oscars)',
        'name_vi': 'Giải Thưởng Viện Hàn Lâm (Oscars)',
        'organization': 'Academy of Motion Picture Arts and Sciences (AMPAS)',
        'country': '🇺🇸 United States',
        'established_year': 1929,
        'latest_ceremony': 'March 15, 2026',
        'category': 'film',
        'badge_icon': 'fa-solid fa-trophy',
        'accent_color': '#f59e0b',
        'description': 'The most prestigious and internationally renowned awards ceremony in the motion picture industry, honoring artistic and technical excellence.',
        'description_vi': 'Giải thưởng điện ảnh danh giá và nổi tiếng bậc nhất hành tinh, tôn vinh những thành tựu nghệ thuật và kỹ thuật xuất sắc nhất của nền điện ảnh.',
        'notable_movie_ids': [872585, 496243, 545611, 238, 424, 122, 597, 13, 274, 98, 6977, 313369]
    },
    {
        'id': 'golden-globes',
        'slug': 'golden-globes',
        'name': 'Golden Globe Awards',
        'name_vi': 'Giải Quả Cầu Vàng (Golden Globes)',
        'organization': 'Hollywood Foreign Press Association (HFPA)',
        'country': '🇺🇸 United States',
        'established_year': 1944,
        'latest_ceremony': 'January 11, 2026',
        'category': 'film',
        'badge_icon': 'fa-solid fa-globe',
        'accent_color': '#eab308',
        'description': 'Accolades bestowed by international journalists recognizing excellence in both domestic and foreign film and American television.',
        'description_vi': 'Giải thưởng uy tín do các nhà báo quốc tế bình chọn, tôn vinh những tác phẩm điện ảnh và truyền hình xuất sắc nhất trong năm.',
        'notable_movie_ids': [872585, 313369, 13, 240, 238, 597, 27205, 157336, 496243, 680]
    },
    {
        'id': 'bafta',
        'slug': 'bafta',
        'name': 'BAFTA Film Awards',
        'name_vi': 'Giải Thưởng Điện Ảnh Viện Hàn Lâm Anh (BAFTA)',
        'organization': 'British Academy of Film and Television Arts',
        'country': '🇬🇧 United Kingdom',
        'established_year': 1949,
        'latest_ceremony': 'February 22, 2026',
        'category': 'film',
        'badge_icon': 'fa-solid fa-masks-theater',
        'accent_color': '#f59e0b',
        'description': 'Annual award show hosted by the British Academy honoring the best British and international contributions to film.',
        'description_vi': 'Giải thưởng thường niên của Viện Hàn lâm Nghệ thuật Điện ảnh và Truyền hình Anh, tôn vinh các đóng góp điện ảnh xuất sắc toàn cầu.',
        'notable_movie_ids': [872585, 424, 496243, 238, 122, 244786, 155, 98, 274, 423]
    },
    {
        'id': 'cannes',
        'slug': 'cannes',
        'name': 'Cannes Film Festival (Palme d\'Or)',
        'name_vi': 'Liên Hoan Phim Cannes (Cành Cọ Vàng)',
        'organization': 'Association Française du Festival International du Film',
        'country': '🇫🇷 France',
        'established_year': 1946,
        'latest_ceremony': 'May 23, 2026',
        'category': 'festival',
        'badge_icon': 'fa-solid fa-leaf',
        'accent_color': '#10b981',
        'description': 'One of the "Big Three" major European film festivals. The Palme d\'Or is among the most coveted artistic prizes in world cinema.',
        'description_vi': 'Một trong ba liên hoan phim quốc tế lớn nhất châu Âu. Giải Cành Cọ Vàng là biểu tượng đỉnh cao của nghệ thuật điện ảnh tác giả.',
        'notable_movie_ids': [496243, 680, 28, 423, 238, 389, 637, 240, 244786]
    },
    {
        'id': 'venice',
        'slug': 'venice',
        'name': 'Venice International Film Festival (Golden Lion)',
        'name_vi': 'Liên Hoan Phim Venice (Sư Tử Vàng)',
        'organization': 'La Biennale di Venezia',
        'country': '🇮🇹 Italy',
        'established_year': 1932,
        'latest_ceremony': 'September 12, 2026',
        'category': 'festival',
        'badge_icon': 'fa-solid fa-crown',
        'accent_color': '#6366f1',
        'description': 'The world\'s oldest film festival and one of the prestigious "Big Three", celebrating boundary-pushing auteur cinema and world premieres.',
        'description_vi': 'Liên hoan phim lâu đời nhất thế giới, tôn vinh những tác phẩm điện ảnh nghệ thuật tiên phong và các buổi công chiếu toàn cầu.',
        'notable_movie_ids': [475557, 313369, 238, 240, 28, 680, 423, 496243]
    },
    {
        'id': 'berlin',
        'slug': 'berlin',
        'name': 'Berlin International Film Festival (Golden Bear)',
        'name_vi': 'Liên Hoan Phim Quốc Tế Berlin (Gấu Vàng)',
        'organization': 'Kulturveranstaltungen des Bundes in Berlin',
        'country': '🇩🇪 Germany',
        'established_year': 1951,
        'latest_ceremony': 'February 25, 2026',
        'category': 'festival',
        'badge_icon': 'fa-solid fa-award',
        'accent_color': '#ec4899',
        'description': 'Known as the Berlinale, one of the world\'s largest public film festivals, championing socially conscious and daring cinematic vision.',
        'description_vi': 'Còn gọi là Berlinale, liên hoan phim tôn vinh những tác phẩm đậm tính nhân văn, xã hội và tư duy điện ảnh đột phá.',
        'notable_movie_ids': [129, 389, 496243, 424, 238, 274, 28, 637]
    },
    {
        'id': 'sag-awards',
        'slug': 'sag-awards',
        'name': 'Screen Actors Guild Awards (Actor Awards)',
        'name_vi': 'Giải Thưởng Nghiệp Đoàn Diễn Viên (SAG Awards)',
        'organization': 'SAG-AFTRA',
        'country': '🇺🇸 United States',
        'established_year': 1995,
        'latest_ceremony': 'March 1, 2026',
        'category': 'guild',
        'badge_icon': 'fa-solid fa-users',
        'accent_color': '#06b6d4',
        'description': 'Presented by performers to honor outstanding individual and ensemble acting performances in film and primetime television.',
        'description_vi': 'Giải thưởng do chính các diễn viên chuyên nghiệp bình chọn, tôn vinh những màn trình diễn xuất sắc nhất của cá nhân và dàn diễn viên.',
        'notable_movie_ids': [872585, 545611, 496243, 13, 274, 424, 98, 6977, 313369]
    },
    {
        'id': 'critics-choice',
        'slug': 'critics-choice',
        'name': 'Critics\' Choice Movie Awards',
        'name_vi': 'Giải Thưởng Bình Chọn Của Các Nhà Phê Bình',
        'organization': 'Critics Choice Association (CCA)',
        'country': '🇺🇸 United States',
        'established_year': 1996,
        'latest_ceremony': 'January 18, 2026',
        'category': 'guild',
        'badge_icon': 'fa-solid fa-star',
        'accent_color': '#8b5cf6',
        'description': 'Bestowed annually by the largest film critics organization in North America to honor the finest achievements in cinematic storytelling.',
        'description_vi': 'Giải thưởng thường niên của Hiệp hội Phê bình Phim lớn nhất Bắc Mỹ, tôn vinh những kiệt tác kể chuyện bằng ngôn ngữ điện ảnh.',
        'notable_movie_ids': [872585, 545611, 313369, 496243, 244786, 155, 27205, 157336]
    },
    {
        'id': 'spirit-awards',
        'slug': 'spirit-awards',
        'name': 'Film Independent Spirit Awards',
        'name_vi': 'Giải Tinh Thần Độc Lập (Spirit Awards)',
        'organization': 'Film Independent',
        'country': '🇺🇸 United States',
        'established_year': 1984,
        'latest_ceremony': 'February 16, 2026',
        'category': 'film',
        'badge_icon': 'fa-solid fa-feather',
        'accent_color': '#3b82f6',
        'description': 'Premier celebration dedicated to independent filmmakers, honoring unique vision, original voices, and innovative storytelling.',
        'description_vi': 'Giải thưởng hàng đầu dành riêng cho dòng phim độc lập, tôn vinh những tiếng nói độc đáo, nguyên bản và đổi mới sáng tạo.',
        'notable_movie_ids': [545611, 244786, 680, 496243, 274, 6977, 389]
    },
    {
        'id': 'national-board-of-review',
        'slug': 'national-board-of-review',
        'name': 'National Board of Review Awards',
        'name_vi': 'Giải Hội Đồng Phê Bình Quốc Gia (NBR)',
        'organization': 'National Board of Review of Motion Pictures',
        'country': '🇺🇸 United States',
        'established_year': 1909,
        'latest_ceremony': 'January 6, 2026',
        'category': 'guild',
        'badge_icon': 'fa-solid fa-scroll',
        'accent_color': '#14b8a6',
        'description': 'A century-old historic association of film enthusiasts, academics, and professionals celebrating the best films and performances.',
        'description_vi': 'Tổ chức điện ảnh hơn 100 năm tuổi quy tụ các học giả và chuyên gia, mở màn cho mùa giải thưởng điện ảnh hàng năm.',
        'notable_movie_ids': [872585, 238, 240, 424, 13, 274, 98, 27205]
    },
    {
        'id': 'emmys',
        'slug': 'emmys',
        'name': 'Primetime Emmy Awards',
        'name_vi': 'Giải Thưởng Truyền Hình Emmy (Emmy Awards)',
        'organization': 'Television Academy',
        'country': '🇺🇸 United States',
        'established_year': 1949,
        'latest_ceremony': 'September 14, 2026',
        'category': 'tv',
        'badge_icon': 'fa-solid fa-tv',
        'accent_color': '#d97706',
        'description': 'The foremost honor in American television recognizing artistic and technical merit across episodic series and television films.',
        'description_vi': 'Giải thưởng danh giá nhất của ngành công nghiệp truyền hình, tôn vinh các tác phẩm phim bộ và chương trình truyền hình đỉnh cao.',
        'notable_movie_ids': [872585, 27205, 157336, 496243, 122, 238]
    },
    {
        'id': 'sundance',
        'slug': 'sundance',
        'name': 'Sundance Film Festival Grand Jury Prize',
        'name_vi': 'Liên Hoan Phim Sundance (Grand Jury Prize)',
        'organization': 'Sundance Institute',
        'country': '🇺🇸 United States',
        'established_year': 1978,
        'latest_ceremony': 'January 25, 2026',
        'category': 'festival',
        'badge_icon': 'fa-solid fa-mountain-sun',
        'accent_color': '#f97316',
        'description': 'The largest independent film festival in the United States, launching landmark careers and cinematic discoveries.',
        'description_vi': 'Liên hoan phim độc lập danh giá nhất Bắc Mỹ, cái nôi nâng tầm những đạo diễn tài ba và tác phẩm điện ảnh kinh điển.',
        'notable_movie_ids': [244786, 680, 545611, 496243, 389, 475557]
    }
]


def get_all_awards(category=None, query=None, sort='popular'):
    """
    Returns filtered and sorted list of awards.
    """
    results = list(AWARDS_CATALOG)

    # Filter by category
    if category and category != 'all':
        results = [a for a in results if a.get('category') == category]

    # Filter by search query
    if query:
        q = query.lower().strip()
        results = [
            a for a in results
            if q in a.get('name', '').lower()
            or q in a.get('name_vi', '').lower()
            or q in a.get('organization', '').lower()
            or q in a.get('country', '').lower()
            or q in a.get('description', '').lower()
            or q in a.get('description_vi', '').lower()
        ]

    # Sort
    if sort == 'alphabetical':
        results.sort(key=lambda x: x.get('name', ''))
    elif sort == 'established':
        results.sort(key=lambda x: x.get('established_year', 0))
    # default: popular (catalog order)

    return results


def get_award_by_slug_data(slug):
    """
    Finds award metadata by slug or id.
    """
    if not slug:
        return None
    slug_clean = str(slug).lower().strip()
    for a in AWARDS_CATALOG:
        if a['slug'] == slug_clean or a['id'] == slug_clean:
            return a
    return None
