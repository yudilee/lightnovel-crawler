import { Descriptions, Grid, Space } from 'antd';
import { ReaderFontFamilySettings } from './FontFamilySettings';
import { ReaderFontSizeSettings } from './FontSizeSettings';
import { ReaderLineHeightSettings } from './LineHeightSettings';
import { ReaderThemeSettings } from './ThemeSettings';
import type { ReaderSettingsItem } from './types';
import { ReaderVoiceSettings } from './VoiceSettings';

const items: ReaderSettingsItem[] = [
  ReaderThemeSettings,
  ReaderFontFamilySettings,
  ReaderFontSizeSettings,
  ReaderLineHeightSettings,
  ReaderVoiceSettings,
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
