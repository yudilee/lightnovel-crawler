import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { ReaderTheme } from '@/types';
import { BgColorsOutlined, CheckOutlined } from '@ant-design/icons';
import { Avatar, Flex, Popover } from 'antd';
import { isEqual, startCase } from 'lodash';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from '.';

export const ReaderThemeSettings: ReaderSettingsItem = {
  label: 'Theme',
  icon: <BgColorsOutlined />,
  component: () => {
    const theme = useSelector(Reader.select.theme);

    const updateTheme = (value: ReaderTheme) => {
      store.dispatch(Reader.action.setTheme(value));
    };

    return (
      <Flex wrap gap={10}>
        {Object.entries(ReaderTheme).map(([name, value]) => (
          <Popover content={startCase(name)}>
            <Avatar
              style={{ ...value, cursor: 'pointer' }}
              onClick={() => updateTheme(value)}
              icon={isEqual(theme, value) && <CheckOutlined />}
            />
          </Popover>
        ))}
      </Flex>
    );
  },
};
