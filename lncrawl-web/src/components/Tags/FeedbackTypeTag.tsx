import { FeedbackTypeLabels } from '@/pages/FeedbackList/utils';
import { FeedbackType } from '@/types/enums';
import { BugOutlined, CommentOutlined, StarOutlined } from '@ant-design/icons';
import { Tag } from 'antd';

export const FeedbackTypeTag: React.FC<{ value: FeedbackType }> = ({
  value,
}) => {
  switch (value) {
    case FeedbackType.GENERAL:
      return (
        <Tag icon={<CommentOutlined />} color="purple">
          {FeedbackTypeLabels[value]}
        </Tag>
      );
    case FeedbackType.ISSUE:
      return (
        <Tag icon={<BugOutlined />} color="red">
          {FeedbackTypeLabels[value]}
        </Tag>
      );
    case FeedbackType.FEATURE:
      return (
        <Tag icon={<StarOutlined />} color="orange">
          {FeedbackTypeLabels[value]}
        </Tag>
      );
    default:
      return null;
  }
};
