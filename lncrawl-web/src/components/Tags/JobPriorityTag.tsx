import { JobPriority } from '@/types';
import { ThunderboltOutlined } from '@ant-design/icons';
import { Tag } from 'antd';

export const JobPriorityTag: React.FC<{ value: JobPriority }> = ({ value }) => {
  switch (value) {
    case JobPriority.LOW:
      return <Tag icon={<ThunderboltOutlined />}>Low Priority</Tag>;
    case JobPriority.NORMAL:
      return (
        <Tag icon={<ThunderboltOutlined />} color="gold">
          Normal Priority
        </Tag>
      );
    case JobPriority.HIGH:
      return (
        <Tag icon={<ThunderboltOutlined />} color="volcano">
          <b>High Priority</b>
        </Tag>
      );
  }
};
