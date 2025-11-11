import { ReaderFontFamilySettings } from './FontFamilySettings';
import { ReaderFontSizeSettings } from './FontSizeSettings';
import { ReaderLineHeightSettings } from './LineHeightSettings';
import { ReaderThemeSettings } from './ThemeSettings';
import { ReaderVoiceSettings } from './VoiceSettings';

export interface ReaderSettingsItem {
  label: string;
  icon: React.ReactNode;
  component: React.FC<any>;
}

export const readerSettingsItems: ReaderSettingsItem[] = [
  ReaderThemeSettings,
  ReaderFontFamilySettings,
  ReaderFontSizeSettings,
  ReaderLineHeightSettings,
  ReaderVoiceSettings,
];
