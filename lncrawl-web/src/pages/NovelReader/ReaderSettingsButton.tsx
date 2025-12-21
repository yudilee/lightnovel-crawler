import { ReaderSettings } from '@/pages/SettingsPage/ReaderSettings';
import { SettingOutlined } from '@ant-design/icons';
import { Drawer, Grid, Modal } from 'antd';
import { useState } from 'react';

export const ReaderSettingsButton: React.FC<
  React.HTMLAttributes<HTMLDivElement>
> = (props) => {
  const { sm, md } = Grid.useBreakpoint();
  const [open, setOpen] = useState<boolean>(false);

  return (
    <>
      <div {...props} onClick={() => setOpen(true)}>
        <SettingOutlined />
        {sm && 'Settings'}
      </div>

      {md ? (
        <Modal
          closable
          centered
          width={600}
          open={open}
          footer={null}
          destroyOnHidden
          title="Reader Settings"
          onCancel={() => setOpen(false)}
          styles={{
            header: {
              paddingBottom: 10,
              background: 'transparent',
            },
          }}
        >
          <ReaderSettings />
        </Modal>
      ) : (
        <Drawer
          open={open}
          closable={false}
          placement="bottom"
          onClose={() => setOpen(false)}
          height={300}
          styles={{
            body: {
              padding: 5,
            },
          }}
        >
          <ReaderSettings />
        </Drawer>
      )}
    </>
  );
};
