export type Lang = 'en' | 'he';

export const t = {
  en: {
    nav: {
      matchExplorer: 'Match Explorer',
      groups: 'Groups',
      bracket: 'Bracket',
      liveOdds: 'Live Odds',
      stats: 'Stats',
    },
    matchExplorer: {
      breadcrumb: 'Home / Matches',
      title: 'Match Explorer',
      subtitle: 'FIFA World Cup 2026',
    },
    groups: {
      breadcrumb: 'Home / Groups',
      title: 'Groups',
      subtitle: 'FIFA World Cup 2026',
      cols: { team: 'Team', mp: 'MP', w: 'W', d: 'D', l: 'L', gf: 'GF', ga: 'GA', gd: 'GD', pts: 'Pts' },
    },
    intel: {
      back: '← Explorer',
      title: 'Match Intelligence & AI Score Predictor',
      fifaRank: 'FIFA Rank',
      homeForm: 'Home Form',
      awayForm: 'Away Form',
      h2h: 'Head to Head',
      odds: 'Live Odds',
      prediction: 'AI Prediction',
    },
  },
  he: {
    nav: {
      matchExplorer: 'לוח משחקים',
      groups: 'בתים',
      bracket: 'עץ טורניר',
      liveOdds: 'הימורים חיים',
      stats: 'סטטיסטיקות',
    },
    matchExplorer: {
      breadcrumb: 'בית / משחקים',
      title: 'לוח משחקים',
      subtitle: 'גביע העולם פיפ״א 2026',
    },
    groups: {
      breadcrumb: 'בית / בתים',
      title: 'בתים',
      subtitle: 'גביע העולם פיפ״א 2026',
      cols: { team: 'נבחרת', mp: 'מש׳', w: 'נצ׳', d: 'תיקו', l: 'הפ׳', gf: 'ש״ז', ga: 'ש״ח', gd: 'הפרש', pts: 'נק׳' },
    },
    intel: {
      back: '← חזרה',
      title: 'ניתוח משחק ומנבא תוצאה',
      fifaRank: 'דירוג פיפ״א',
      homeForm: 'פורמה בית',
      awayForm: 'פורמה חוץ',
      h2h: 'גברת על גברת',
      odds: 'הימורים חיים',
      prediction: 'ניבוי בינה מלאכותית',
    },
  },
} as const;

export const teamNames: Record<string, string> = {
  // Group A
  'Mexico': 'מקסיקו',
  'South Africa': 'דרום אפריקה',
  'South Korea': 'קוריאה הדרומית',
  'Czechia': 'צ׳כיה',
  // Group B
  'Canada': 'קנדה',
  'Bosnia & Herzegovina': 'בוסניה והרצגובינה',
  'Qatar': 'קטר',
  'Switzerland': 'שוויץ',
  // Group C
  'Brazil': 'ברזיל',
  'Morocco': 'מרוקו',
  'Haiti': 'האיטי',
  'Scotland': 'סקוטלנד',
  // Group D
  'USA': 'ארה״ב',
  'Paraguay': 'פרגוואי',
  'Australia': 'אוסטרליה',
  'Turkey': 'טורקיה',
  // Group E
  'Germany': 'גרמניה',
  'Curacao': 'קוראסאו',
  'Ivory Coast': 'חוף השנהב',
  'Ecuador': 'אקוודור',
  // Group F
  'Netherlands': 'הולנד',
  'Japan': 'יפן',
  'Sweden': 'שוודיה',
  'Tunisia': 'תוניסיה',
  // Group G
  'Belgium': 'בלגיה',
  'Egypt': 'מצרים',
  'Iran': 'איראן',
  'New Zealand': 'ניו זילנד',
  // Group H
  'Spain': 'ספרד',
  'Cape Verde': 'כף ורדה',
  'Saudi Arabia': 'ערב הסעודית',
  'Uruguay': 'אורוגוואי',
  // Group I
  'France': 'צרפת',
  'Senegal': 'סנגל',
  'Iraq': 'עיראק',
  'Norway': 'נורווגיה',
  // Group J
  'Argentina': 'ארגנטינה',
  'Algeria': 'אלג׳יריה',
  'Austria': 'אוסטריה',
  'Jordan': 'ירדן',
  // Group K
  'Portugal': 'פורטוגל',
  'DR Congo': 'קונגו הדמוקרטית',
  'Uzbekistan': 'אוזבקיסטן',
  'Colombia': 'קולומביה',
  // Group L
  'England': 'אנגליה',
  'Croatia': 'קרואטיה',
  'Ghana': 'גאנה',
  'Panama': 'פנמה',
};

export function translateTeam(name: string, lang: Lang): string {
  return lang === 'he' ? (teamNames[name] ?? name) : name;
}

export function translateGroup(group: string, lang: Lang): string {
  if (lang !== 'he') return group;
  return group.replace('Group', 'בית');
}
