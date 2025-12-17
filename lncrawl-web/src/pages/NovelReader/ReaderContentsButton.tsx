import type { Chapter } from '@/types';
import { stringifyError } from '@/utils/errors';
import { UnorderedListOutlined } from '@ant-design/icons';
import { Button, Descriptions, Grid, message, Modal } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const ReaderContentsButton: React.FC<{
  novelId: string;
}> = ({ novelId }) => {
  const location = useLocation();
  const { sm } = Grid.useBreakpoint();
  const [messageApi, contextHolder] = message.useMessage();

  const [open, setOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [chapters, setChapters] = useState<Chapter[]>([]);

  useEffect(() => {
    setOpen(false);
  }, [location]);

  const fetchChapters = async () => {
    try {
      setOpen(true);
      if (!chapters.length) {
        setLoading(true);
        const { data } = await axios.get<Chapter[]>(
          `/api/novel/${novelId}/chapters`
        );
        setChapters(data);
      }
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Button
        size="large"
        style={{ borderRadius: 0 }}
        icon={<UnorderedListOutlined />}
        loading={loading}
        onClick={fetchChapters}
      >
        {sm && 'Contents'}
      </Button>

      <Modal
        closable
        centered
        open={open}
        width={600}
        footer={null}
        destroyOnHidden
        loading={loading}
        title="Table of Contents"
        onCancel={() => setOpen(false)}
        style={{ padding: 15 }}
      >
        <Descriptions
          column={1}
          labelStyle={{
            width: 30,
            justifyContent: 'flex-end',
          }}
          items={chapters.map((chapter) => ({
            key: chapter.id,
            label: chapter.serial,
            children: <Link to={`/read/${chapter.id}`}>{chapter.title}</Link>,
          }))}
        />
      </Modal>
    </>
  );
};
