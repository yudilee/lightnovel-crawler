import { Descriptions, Grid, Space } from 'antd';
import { ReaderFontFamilySettings } from './FontFamilySettings';
import { ReaderFontSizeSettings } from './FontSizeSettings';
import { ReaderLineHeightSettings } from './LineHeightSettings';
import { ReaderThemeSettings } from './ThemeSettings';
import type { ReaderSettingsItem } from './types';
import { ReaderVoicePitchSettings } from './VoicePitch';
import { ReaderVoiceSettings } from './VoiceSettings';
import { ReaderVoiceSpeedSettings } from './VoiceSpeed';
import { ReaderAutoFetchSetting } from './AutoFetchSetting';

const items: ReaderSettingsItem[] = [
  // ReaderLayoutSettings,
  ReaderThemeSettings,
  ReaderFontFamilySettings,
  ReaderFontSizeSettings,
  ReaderLineHeightSettings,
  ReaderVoiceSettings,
  ReaderVoicePitchSettings,
  ReaderVoiceSpeedSettings,
  ReaderAutoFetchSetting,
];

export const ReaderSettings = () => {
  const { sm } = Grid.useBreakpoint();
  return (
    <Descriptions
      bordered
      column={1}
      size="small"
      layout={sm ? 'horizontal' : 'vertical'}
      items={items.map((item) => ({
        label: (
          <Space>
            {item.icon}
            {item.label}
          </Space>
        ),
        children: <item.component />,
      }))}
    />
  );
};
