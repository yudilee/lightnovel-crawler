import type { Library, Novel } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DeleteOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import axios from 'axios';

export const RemoveLibraryNovelButton: React.FC<{
  novel: Novel;
  library: Library;
}> = ({ novel, library }) => {
  const [messageApi, contextHolder] = message.useMessage();

  const handleRemove = async (novel: Novel) => {
    try {
      await axios.delete(`/api/library/${library.id}/novels/${novel.id}`);
      messageApi.success('Novel removed');
    } catch (err) {
      messageApi.error(stringifyError(err));
    }
  };

  return (
    <>
      {contextHolder}
      <Button
        icon={<DeleteOutlined />}
        danger
        type="primary"
        size="small"
        style={{
          position: 'absolute',
          top: 4,
          right: 4,
          zIndex: 2,
        }}
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
          handleRemove(novel);
        }}
      />
    </>
  );
};
