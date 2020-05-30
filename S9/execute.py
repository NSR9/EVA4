from tqdm import tqdm
import numpy as np
import torch.nn.functional as F
import torch
import torch.optim as optim

import torch.nn as nn
class Test_Train():
  def __init__(self):

# # This is to hold all the values and plot some graphs to extract few good insights.
    self.train_losses = []
    self.test_losses = []
    self.train_acc = []
    self.test_acc = []
    self.train_epoch_end = []
    self.test_loss_min = np.inf # setting it to infinity(max value)
    global criterion
    criterion =  nn.CrossEntropyLoss()
    # when the test loss becomes min I will save the particular model


  def train(self, model, device, trainloader, optimizer, epoch,scheduler):
    model.train()    # prepare model for training
    pbar = tqdm(trainloader)
    #correct = 0
    processed = 0
    correct = 0
  
    for batch_idx, (data, target) in enumerate(pbar): # passing on data & target values to device
      data, target = data.to(device), target.to(device)
      optimizer.zero_grad()    # clear the gradients of all optimized variables
      
      # Predict
      y_pred = model(data)   # forward pass

      # nll loss calculation  Calculate loss
      #loss = F.nll_loss(y_pred, target)

     

      # cross entropy loss calculation 
      loss = criterion(y_pred, target)





      # #Implementing L1 Regularization
      # if L1lambda:
      #   with torch.enable_grad():
      #     l1_loss = 0.
      #     for param in model.parameters():
      #       l1_loss += torch.sum(param.abs())
      #     loss += L1lambda * l1_loss

      self.train_losses.append(loss)

      # Backpropagation
      loss.backward()   # backward pass: compute gradient of the loss with respect to model parameters
      optimizer.step()   # perform a single optimization step (parameter update)

      # Update pbar-tqdm
    
      # pred = y_pred.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
      _, predicted = torch.max(y_pred.data, 1)
      # correct += pred.eq(target.view_as(pred)).sum().item()
      correct += (predicted == target).sum().item()
      processed += len(data)
      pbar.set_description(desc= f'Loss={loss.item()} Batch_id={batch_idx} Accuracy={100*correct/processed:0.2f}')

      # pbar.set_description(desc= f'Loss={loss.item()} Batch_id={batch_idx} Accuracy={100*correct/processed:0.2f}')
      self.train_acc.append(100*correct/processed)
      scheduler.step()
      self.train_epoch_end.append(self.train_acc[-1])



      
    
          
     
            
     
     


  def test(self, model, device, testloader,incorrect_samples,filename): 
      model.eval()  # prep model for evaluation
      test_loss = 0
      correct = 0
      with torch.no_grad():
          for data, target in testloader:
            img_batch = data
            data, target = data.to(device), target.to(device)
            output = model(data)  # forward pass: compute predicted outputs by passing inputs to the model
            #test_loss += torch.nn.functional.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            test_loss += criterion(output, target)
            _, predicted = torch.max(output.data, 1)
           
            correct += (predicted == target).sum().item()

            result = predicted.eq(target.view_as(predicted))

            # This is to extract incorrect samples/misclassified images
            if len(incorrect_samples) < 25:
              for i in range(0, testloader.batch_size):
                if not list(result)[i]:
                  incorrect_samples.append({'prediction': list(predicted)[i], 'label': list(target.view_as(predicted))[i],'image': img_batch[i]})

      test_loss /= len(testloader.dataset)
      self.test_losses.append(test_loss)

      # save model if validation loss has decreased
      if test_loss <= self.test_loss_min:
          print('Validation loss has  decreased ({:.4f} --> {:.4f}).  Saving model ...'.format(self.test_loss_min, test_loss))
          torch.save(model.state_dict(), filename)
          self.test_loss_min = test_loss


      print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(
          test_loss, correct, len(testloader.dataset),
          100. * correct / len(testloader.dataset)))
    
      self.test_acc.append(100. * correct / len(testloader.dataset))