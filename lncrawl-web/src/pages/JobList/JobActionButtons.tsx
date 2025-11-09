import { Auth } from '@/store/_auth';
import { type Job } from '@/types';
import { stringifyError } from '@/utils/errors';
import { CloseOutlined, ReloadOutlined } from '@ant-design/icons';
import { Button, message, type ButtonProps } from 'antd';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

export const JobActionButtons: React.FC<{
  job: Job;
  onChange?: () => any;
  size?: ButtonProps['size'];
}> = ({ job, size, onChange }) => {
  const navigate = useNavigate();
  const isAdmin = useSelector(Auth.select.isAdmin);
  const currentUser = useSelector(Auth.select.user);
  const [messageApi, contextHolder] = message.useMessage();

  const cancelJob = async () => {
    try {
      await axios.post(`/api/job/${job.id}/cancel`);
      if (onChange) onChange();
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err, 'Something went wrong!'),
      });
    }
  };

  const replayJob = async () => {
    try {
      const result = await axios.post<Job>(`/api/job/${job.id}/replay`, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      navigate({ pathname: `/job/${result.data.id}` });
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err, 'Something went wrong!'),
      });
    }
  };

  return (
    <>
      {contextHolder}
      {job.is_done && (
        <Button size={size} onClick={replayJob}>
          <ReloadOutlined /> Replay
        </Button>
      )}
      {(isAdmin || job.user_id === currentUser?.id) && job.is_done && (
        <Button size={size} danger onClick={cancelJob}>
          <CloseOutlined /> Cancel
        </Button>
      )}
    </>
  );
};
