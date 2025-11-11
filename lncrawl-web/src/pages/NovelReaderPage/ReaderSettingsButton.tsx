import { SettingOutlined } from '@ant-design/icons';
import { Button, Descriptions, Grid, Modal, Space } from 'antd';
import { useState } from 'react';
import { readerSettingsItems } from './settings';

export const ReaderSettingsButton: React.FC<any> = () => {
  const { sm } = Grid.useBreakpoint();
  const [open, setOpen] = useState<boolean>(false);

  return (
    <>
      <Button
        size="large"
        style={{ borderRadius: 0 }}
        icon={<SettingOutlined />}
        onClick={() => setOpen(true)}
      >
        {sm && 'Settings'}
      </Button>

      <Modal
        closable
        centered
        open={open}
        footer={null}
        destroyOnHidden
        title="Reader Settings"
        onCancel={() => setOpen(false)}
        styles={{
          header: { paddingBottom: 10 },
          content: { padding: sm ? 20 : '15px 10px' },
        }}
      >
        <Descriptions
          bordered
          column={1}
          size="small"
          layout={sm ? 'horizontal' : 'vertical'}
          items={readerSettingsItems.map((item) => ({
            label: (
              <Space>
                {item.icon}
                {item.label}
              </Space>
            ),
            children: <item.component />,
          }))}
        />
      </Modal>
    </>
  );
};
