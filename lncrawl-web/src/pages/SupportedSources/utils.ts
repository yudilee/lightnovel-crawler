export const getLanguageLabel = (lang?: string) => {
  if (!lang || lang.length !== 2) {
    return 'Any';
  }
  const names = new Intl.DisplayNames(['en'], {
    type: 'language',
  });
  return names.of(lang) || '';
};
