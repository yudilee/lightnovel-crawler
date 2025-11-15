import { ReaderSettings } from '@/pages/SettingsPage/ReaderSettings';
import { SettingOutlined } from '@ant-design/icons';
import { Collapse, Typography, type CollapseProps } from 'antd';
import { NotificationSettings } from './NotificationSettings';

const items: CollapseProps['items'] = [
  {
    key: 'reader',
    label: 'Reader',
    children: <ReaderSettings />,
  },

  {
    key: 'notifications',
    label: 'Notifications',
    children: <NotificationSettings />,
  },
];

const allKeys = items.map((x) => String(x.key)).filter(Boolean);

export const SettingsPage: React.FC<any> = () => {
  return (
    <>
      <Typography.Title level={2}>
        <SettingOutlined /> Settings
      </Typography.Title>

      <Collapse defaultActiveKey={allKeys} items={items} />
    </>
  );
};
